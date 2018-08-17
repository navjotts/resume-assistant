const xmldom = require('xmldom');
const jszip = require('jszip');

const Utils = require('./Utils.js');

class Paragraph {
    constructor () {
        this.text = '';
    }
}

class DocxParser {
    constructor () {
        this.doc = []; // array of paragraphs
        this.xmlContent = new Map(); // xmlFile => xmlContent
        this.mediaContent = new Map(); // mediaFile => buffer
    }

    static async parseAsync(file) {
        return await Utils.promisify(function(cb) {
            DocxParser.parse(file, cb);
        }, null);
    }

    static parse(file, cb) {
        let parser = new DocxParser();
        let zippedFileCount = 0;

        function addXML(file) {
            if (file.name.indexOf('media/') != -1) {
                file.async("arraybuffer").then(function(fileContent) {
                    parser.mediaContent.set(file.name, fileContent);
                    parseIfReady();
                }).catch(function() {});
            }
            else {
                file.async("string").then(function(fileContent) {
                    parser.xmlContent.set(file.name, fileContent);
                    parseIfReady();
                }).catch(function() {});
            }
        }

        function parseIfReady() {
            if (parser.mediaContent.size + parser.xmlContent.size == zippedFileCount) {
                parser.parse(function(err, doc) {
                    cb(err, doc);
                });
            }
        }

        jszip.loadAsync(file).then(function(content) {
            zippedFileCount = Object.keys(content.files).length;
            for (let fileName in content.files) {
                addXML(content.files[fileName]);
            }
        });
    }

    parse(cb) {
        this.parseDocBody();
        cb(null, this.doc);
    }

    parseDocBody() {
        let docxXml = new xmldom.DOMParser().parseFromString(this.xmlContent.get('word/document.xml'));
        let bodyNode = docxXml.getElementsByTagName(docxXml.documentElement.prefix + ':body')[0];
        this.parsePageChildren(bodyNode);
    }

    parsePageChildren(rootNode) {
        for (let childNodeNo = 0; childNodeNo < rootNode.childNodes.length; ++childNodeNo) {
            let childNode = rootNode.childNodes[childNodeNo];

            if (childNode.localName == 'p') {
                let para = new Paragraph();
                this.doc.push(para);
                this.parseParagraphChildren(childNode, para);
            }
            else if (childNode.localName == 'tbl') {
                this.parseTable(childNode);
            }
            else if (childNode.localName == 'sdt') {
                this.parseBlockLevelSDT(childNode);
            }
        }
    }

    parseParagraphChildren(rootNode, paragraph) {
        let runningPara = paragraph;

        for (let childNodeNo = 0; childNodeNo < rootNode.childNodes.length; ++childNodeNo) {
            let childNode = rootNode.childNodes[childNodeNo];

            if (childNode.localName == 'r' || childNode.localName == 'smartTag' || childNode.localName == 'sdt') {
                if (childNode.localName == 'r') {
                    runningPara = this.parseRun(childNode, runningPara);
                }
                else if (childNode.localName == 'smartTag') {
                    runningPara = this.parseParagraphChildren(childNode, runningPara);
                }
                else if (childNode.localName == 'sdt') {
                    let sdtContentNode = childNode.getElementsByTagName(childNode.prefix + ':sdtContent')[0];
                    runningPara = this.parseParagraphChildren(sdtContentNode, runningPara);
                }
            }
            else if (childNode.localName == 'hyperlink') {
                if (!this.parseExternalHyperlink(childNode, paragraph)) {
                    this.parseInternalHyperlink(childNode, paragraph);
                }
            }
        }
    }

    parseRun(rootNode, paragraph) {
        let runningPara = paragraph;

        for (let childNodeNo = 0; childNodeNo < rootNode.childNodes.length; ++childNodeNo) {
            let childNode = rootNode.childNodes[childNodeNo];

            if (childNode.localName == 't') {
                runningPara.text += childNode.textContent;
            }
            else if (childNode.localName == 'tab') {
                runningPara.text += ' ';
            }
            else if (childNode.localName == 'AlternateContent') {
                runningPara = this.parseAltContentElement(childNode, runningPara);
            }
            else if (childNode.localName == 'br' || childNode.localName == 'cr') {
                runningPara = new Paragraph();
                this.doc.push(runningPara);
            }
        }

        return runningPara;
    }

    parseAltContentElement(rootNode, paragraph) {
        let runningPara = paragraph;
        let choiceNode = rootNode.getElementsByTagName('mc:Choice')[0];
        let fallbackNode = rootNode.getElementsByTagName('mc:Fallback')[0];
        if (fallbackNode) {
            runningPara = this.parseFallbackElement(fallbackNode, runningPara);
        }
        else if (choiceNode) {
            runningPara = this.parseChoiceElement(choiceNode, runningPara);
        }

        return runningPara;
    }

    parseChoiceElement(choiceNode, paragraph) {
        let runningPara = paragraph;

        let drawingNode = choiceNode.getElementsByTagName('w:drawing')[0];
        let imageNode = drawingNode.getElementsByTagName('wp:inline')[0];
        if (!imageNode) {
            imageNode = drawingNode.getElementsByTagName('wp:anchor')[0];
        }

        let graphicNode = imageNode.getElementsByTagName('a:graphic')[0];
        let graphicDataNode = graphicNode.getElementsByTagName('a:graphicData')[0];
        let shapeNode = graphicDataNode.getElementsByTagName('wps:wsp')[0];
        if (shapeNode) {
            let txbxNode = shapeNode.getElementsByTagName('wps:txbx')[0];
            if (txbxNode) {
                let txbxContentNode = txbxNode.getElementsByTagName('w:txbxContent')[0];
                if (txbxContentNode) {
                    runningPara = this.parseTextbox(txbxContentNode, runningPara);
                }
            }
        }
    }

    parseFallbackElement(fallbackNode, paragraph) {
        let runningPara = paragraph;
        let pictNode = fallbackNode.getElementsByTagName('w:pict')[0];
        if (pictNode) {
            for (let childNodeNo = 0; childNodeNo < pictNode.childNodes.length; ++childNodeNo) {
                let childNode = pictNode.childNodes[childNodeNo];
                if (childNode.localName == 'rect' || childNode.localName == 'roundrect' || childNode.localName == 'shape') {
                    let textboxNode = childNode.getElementsByTagName('v:textbox')[0];
                    if (textboxNode) {
                        let txbxContentNode = textboxNode.getElementsByTagName('w:txbxContent')[0];
                        if (txbxContentNode) {
                            runningPara = this.parseTextbox(txbxContentNode, runningPara);
                        }
                    }
                }
            }
        }

        return runningPara;
    }

    parseTextbox(txbxContentNode, paragraph) {
        // txbxContent can have PageItems inside them
        this.parsePageChildren(txbxContentNode);
        runningPara = new Paragraph();
        return runningPara;
    }

    parseExternalHyperlink(rootNode, paragraph) {
        let rIdAttr = rootNode.getAttributeNode('r:id');
        if (!rIdAttr) {
            return false;
        }

        for (let childNodeNo = 0; childNodeNo < rootNode.childNodes.length; ++childNodeNo) {
            let childNode = rootNode.childNodes[childNodeNo];
            if (childNode.localName == 'r') {
                this.parseRun(childNode, paragraph);
            }
        }

        return true;
    }

    parseInternalHyperlink(rootNode, paragraph) {
        let anchorAttr = rootNode.getAttributeNode(rootNode.prefix + ':anchor');
        if (!anchorAttr) {
            return false;
        }

        for (let childNodeNo = 0; childNodeNo < rootNode.childNodes.length; ++childNodeNo) {
            let childNode = rootNode.childNodes[childNodeNo];
            if (childNode.localName == 'r') {
                this.parseRun(childNode, paragraph);
            }
        }

        return true;
    }

    parseTable(rootNode) {
        for (let childNodeNo = 0; childNodeNo < rootNode.childNodes.length; ++childNodeNo) {
            let childNode = rootNode.childNodes[childNodeNo];
            if (childNode.localName == 'tr') {
                this.parseTableRow(childNode);
            }
        }
    }

    parseTableRow(rootNode) {
        for (let childNodeNo = 0; childNodeNo < rootNode.childNodes.length; ++childNodeNo) {
            let childNode = rootNode.childNodes[childNodeNo];
            if (childNode.localName == 'tc') {
                this.parseTableCell(childNode);
            }
        }
    }

    parseTableCell(rootNode) {
        this.parsePageChildren(rootNode);
    }

    parseBlockLevelSDT(rootNode) {
        let sdtContentNode = rootNode.getElementsByTagName(rootNode.prefix + ':sdtContent')[0];
        if (sdtContentNode) {
            this.parsePageChildren(sdtContentNode);
        }
    }
}

module.exports = DocxParser;
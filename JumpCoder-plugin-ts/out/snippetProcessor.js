"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.processSelectedSnippet = processSelectedSnippet;
const vscode = __importStar(require("vscode"));
// Type guard function to check if an object is of type ProcessedSnippetResponse
function isProcessedSnippetResponse(data) {
    return typeof data === 'object' && data !== null && 'processedSnippet' in data;
}
async function processSelectedSnippet(editor) {
    const selection = editor.selection;
    const selectedText = editor.document.getText(selection);
    const config = vscode.workspace.getConfiguration('myExtension');
    const serverAddress = config.get('serverAddress');
    console.log(serverAddress);
    try {
        const response = await fetch(`${serverAddress}/api/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompts: selectedText })
        });
        if (!response.ok) {
            throw new Error(`Server error: ${response.statusText}`);
        }
        const data = await response.json();
        // console.log(data);
        // if (!isProcessedSnippetResponse(data)) {
        //     throw new Error('Unexpected response format');
        // }
        // Replace the selected text with the processed snippet
        await editor.edit(editBuilder => {
            editBuilder.replace(selection, data.processedSnippet);
        });
    }
    catch (error) {
        const errorMessage = (error instanceof Error) ? error.message : 'Unknown error occurred';
        vscode.window.showErrorMessage(`Failed to process snippet: ${errorMessage}`);
    }
}
//# sourceMappingURL=snippetProcessor.js.map
import * as vscode from 'vscode';

interface ProcessedSnippetResponse {
    generate_outputs: string;
}

// Type guard function to check if an object is of type ProcessedSnippetResponse
function isProcessedSnippetResponse(data: any): data is ProcessedSnippetResponse {
    return typeof data === 'object' && data !== null && 'processedSnippet' in data;
}

export async function processSelectedSnippet(editor: vscode.TextEditor) {
    const selection = editor.selection;
    const selectedText = editor.document.getText(selection);
    const config = vscode.workspace.getConfiguration('myExtension');
    const serverAddress = config.get<string>('serverAddress');
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

        const data: any = await response.json();
        // console.log(data);
        // if (!isProcessedSnippetResponse(data)) {
        //     throw new Error('Unexpected response format');
        // }

        // Replace the selected text with the processed snippet
        await editor.edit(editBuilder => {
            editBuilder.replace(selection, data.processedSnippet);
        });
    } catch (error) {
        const errorMessage = (error instanceof Error) ? error.message : 'Unknown error occurred';
        vscode.window.showErrorMessage(`Failed to process snippet: ${errorMessage}`);
    }
}

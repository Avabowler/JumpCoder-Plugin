import * as vscode from 'vscode';
import axios from 'axios';

interface SearchParams {
    prompts: string;
    kPositions: string; // 如果需要转换为数字，可以使用 number
    thresholdImprovement: string;
    similarThreshold: string;
    temperature: string;
}


export class SidebarViewProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'mySidebarView';
    private _view?: vscode.WebviewView;

    constructor(private readonly _extensionUri: vscode.Uri) {}

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        webviewView.webview.html = this.getWebviewContent(webviewView.webview);

        webviewView.webview.onDidReceiveMessage(
            message  => {
            switch (message.command) {
                case 'search':
                    const searchParams: SearchParams = message.params;
                    console.log("Received search parameters:", searchParams);
                    performSearch(webviewView, searchParams!);
                    // webviewView.webview.postMessage({ command: 'displayResult', result: `Result for: ${message.text}` });
                    return;
            }
        });
    }

    private getWebviewContent(webview: vscode.Webview): string {
        return `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Search Page</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    display: flex;
                    flex-direction: column; /* 改为上下布局 */
                    justify-content: space-between;
                    color: #000;
                    background-color: #f9f9f9;
                    height: 100vh; /* 保持内容垂直填满整个页面 */
                }
                #container {
                    display: flex;
                    flex-direction: column; /* 改为上下布局 */
                    height: 100%;
                }
                #left-pane, #right-pane {
                    flex: 1;
                    margin: 10px;
                    padding: 10px;
                    border: 1px solid #ccc;
                    border-radius: 8px;
                    background-color: #fff;
                }
                #left-pane {
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                }
                #output {
                    margin-top: 20px;
                    font-size: 16px;
                    color: #000;
                    white-space: pre-wrap;
                }
                .control-group {
                    margin-bottom: 0px;
                    width: 100%;
                }
                .control-group label {
                    display: block;
                    margin-bottom: 0px;
                    font-weight: bold;
                    color: #000;
                }
                .control-group textarea, .control-group input[type="range"] {
                    width: 100%;
                    padding: 8px;
                    border-radius: 4px;
                    border: 1px solid #ccc;
                    font-family: monospace;
                    box-sizing: border-box;
                }
                .control-group span {
                    margin-left: 10px;
                    font-weight: bold;
                    color: #007acc;
                }
                .submit-button {
                    width: 100%;
                    padding: 10px 20px;
                    font-size: 16px;
                    color: #fff;
                    background-color: #007acc;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                .submit-button:hover {
                    background-color: #005f99;
                }
            </style>
        </head>
        <body>
            <div id="container">
                <div id="left-pane">
                    <h3>prompts</h3>
                    <textarea id="searchBox" title="Enter your prompts here. This will be sent to the backend for processing." placeholder="Enter your prompts here..." rows="5"></textarea>
                    <div class="control-group">
                        <label for="k_positions">k_positions <span id="k_positions_value">5</span></label>
                        <input type="range" id="k_positions" name="k_positions" class="slider" min="1" max="10" value="5" title="Adjust the k_positions value.">
                    </div>
                    <div class="control-group">
                        <label for="threshold_improvement">threshold_improvement <span id="threshold_improvement_value">0.85</span></label>
                        <input type="range" id="threshold_improvement" name="threshold_improvement" class="slider" min="0" max="1" step="0.01" value="0.85" title="Set the threshold improvement level.">
                    </div>
                    <div class="control-group">
                        <label for="similar_threshold">similar_threshold <span id="similar_threshold_value">0.3</span></label>
                        <input type="range" id="similar_threshold" name="similar_threshold" class="slider" min="0" max="1" step="0.01" value="0.3" title="Adjust the similarity threshold.">
                    </div>
                    <div class="control-group">
                        <label for="temperature">temperature <span id="temperature_value">0.1</span></label>
                        <input type="range" id="temperature" name="temperature" class="slider" min="0" max="1" step="0.1" value="0.1" title="Set the temperature for sampling.">
                    </div>
                    <button id="searchButton" class="submit-button" title="Click to submit your inputs and parameters.">Submit</button>
                </div>
                <div id="right-pane">
                    <h3>output</h3>
                    <div id="output" title="This area displays the results from the backend.">
                        <!-- Search results will be displayed here -->
                    </div>
                </div>
            </div>
    
            <script>
                const vscode = acquireVsCodeApi();
    
                // 更新滑动条数值的函数
                function updateSliderValue(sliderId, valueId) {
                    const slider = document.getElementById(sliderId);
                    const valueSpan = document.getElementById(valueId);
                    valueSpan.textContent = slider.value;
    
                    slider.addEventListener('input', () => {
                        valueSpan.textContent = slider.value;
                    });
                }
    
                // 初始化滑动条数值显示
                updateSliderValue('k_positions', 'k_positions_value');
                updateSliderValue('threshold_improvement', 'threshold_improvement_value');
                updateSliderValue('similar_threshold', 'similar_threshold_value');
                updateSliderValue('temperature', 'temperature_value');
    
                document.getElementById('searchButton').addEventListener('click', () => {
                    const prompts = document.getElementById('searchBox').value;
                    const kPositions = document.getElementById('k_positions').value;
                    const thresholdImprovement = document.getElementById('threshold_improvement').value;
                    const similarThreshold = document.getElementById('similar_threshold').value;
                    const temperature = document.getElementById('temperature').value;
    
                    const searchParams = {
                        prompts,
                        kPositions,
                        thresholdImprovement,
                        similarThreshold,
                        temperature
                    };
    
                    vscode.postMessage({ command: 'search',params: searchParams});
    
                    // 显示用户输入的内容
                    // document.getElementById('output').innerText = "Submitting with params: " + JSON.stringify(searchParams, null, 2);
                });
    
                // 监听来自扩展的消息
                window.addEventListener('message', event => {
                    const message = event.data;
                    switch (message.command) {
                        case 'displayResult':
                            document.getElementById('output').innerText = message.result;
                            break;
                    }
                });
            </script>
        </body>
        </html>`;
    }
    
}

async function performSearch(panel: vscode.WebviewView, params: SearchParams): Promise<void> {
    const config = vscode.workspace.getConfiguration('myExtension');
    const serverAddress = config.get<string>('serverAddress');
    console.log(serverAddress);
    try {
        
        vscode.window.showInformationMessage(`Search inputs: ${params.prompts}`);        
        const response = await axios.post(`${serverAddress}/api/generate`,  {"prompts": params.prompts,"k_positions": params.kPositions, "threshold_improvement": params.thresholdImprovement,"similar_threshold":params.similarThreshold} );
        vscode.window.showInformationMessage(`Search Results: ${response.data}`);
        
        // 向Webview发送消息，显示后端返回的数据
        panel.webview.postMessage({ command: 'displayResult', result: response.data['generate_outputs']});
    } catch (error) {
        vscode.window.showErrorMessage(`Search failed: ${error}`);
    }
}

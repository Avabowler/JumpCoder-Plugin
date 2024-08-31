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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const axios_1 = __importDefault(require("axios"));
const SidebarViewProvider_1 = require("./SidebarViewProvider");
const snippetProcessor_1 = require("./snippetProcessor");
function activate(context) {
    let disposable = vscode.commands.registerCommand('extension.openSearchPage', () => {
        const panel = vscode.window.createWebviewPanel('searchPage', // 内部标识符
        'Search Page', // 面板标题
        vscode.ViewColumn.One, // 显示在编辑器的哪个视图列中
        {
            enableScripts: true // 启用Webview中的JavaScript
        });
        panel.webview.html = getWebviewContent();
        // 监听来自Webview的消息
        panel.webview.onDidReceiveMessage(message => {
            switch (message.command) {
                case 'search':
                    const searchParams = message.params;
                    console.log("Received search parameters:", searchParams);
                    performSearch(panel, searchParams);
                    return;
            }
        }, undefined, context.subscriptions);
    });
    context.subscriptions.push(disposable);
    // 另一个功能
    const sidebarProvider = new SidebarViewProvider_1.SidebarViewProvider(context.extensionUri);
    context.subscriptions.push(vscode.window.registerWebviewViewProvider(SidebarViewProvider_1.SidebarViewProvider.viewType, sidebarProvider));
    console.log('Extension "SideBar" is now active!');
    const processSnippetCommand = vscode.commands.registerTextEditorCommand('extension.processSnippet', snippetProcessor_1.processSelectedSnippet);
    context.subscriptions.push(processSnippetCommand);
    console.log('Extension "Select" is now active!');
}
function getWebviewContent() {
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
                    flex-direction: row;
                    justify-content: space-between;
                    color: #000; /* 设置页面的默认文本颜色为黑色 */
                    background-color: #f9f9f9;
                }
                #container {
                    display: flex;
                    flex-direction: row;
                    width: 100%;
                }
                #left-pane, #right-pane {
                    flex: 1;
                    margin: 10px;
                    padding: 10px;
                    border: 1px solid #ccc;
                    border-radius: 8px;
                    background-color: #fff; /* 面板背景色为白色，确保文本对比度 */
                }
                #left-pane {
                    max-width: 50%;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                }
                #right-pane {
                    max-width: 50%;
                }
                #output {
                    margin-top: 20px;
                    font-size: 16px;
                    color: #000; /* 保证输出文本为黑色 */
                    white-space: pre-wrap; /* 保留换行和缩进 */
                }
                .control-group {
                    margin-bottom: 5px;
                    width: 100%;
                }
                .control-group span {
                    margin-left: 10px;
                    font-weight: bold;
                    color: #007acc;
                }
                .control-group label {
                    display: block;
                    margin-bottom: 5px;
                    font-weight: bold;
                    color: #000; /* 保证标签文本为黑色 */
                }
                .control-group textarea, .control-group input[type="range"] {
                    width: 100%;
                    padding: 8px;
                    border-radius: 4px;
                    border: 1px solid #ccc;
                    font-family: monospace;
                    box-sizing: border-box; /* 确保padding不会超出宽度 */
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
async function performSearch(panel, params) {
    try {
        const config = vscode.workspace.getConfiguration('myExtension');
        const serverAddress = config.get('serverAddress');
        console.log(serverAddress);
        vscode.window.showInformationMessage(`Search inputs: ${params.prompts}`);
        const response = await axios_1.default.post(`${serverAddress}/api/generate`, { "prompts": params.prompts, "k_positions": params.kPositions, "threshold_improvement": params.thresholdImprovement, "similar_threshold": params.similarThreshold });
        vscode.window.showInformationMessage(`Search Results: ${response.data}`);
        // 向Webview发送消息，显示后端返回的数据
        panel.webview.postMessage({ command: 'displayResult', result: response.data['generate_outputs'] });
    }
    catch (error) {
        vscode.window.showErrorMessage(`Search failed: ${error}`);
    }
}
function deactivate() { }
//# sourceMappingURL=extension.js.map
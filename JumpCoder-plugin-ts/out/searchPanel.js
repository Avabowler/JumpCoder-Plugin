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
exports.SearchPanel = void 0;
const vscode = __importStar(require("vscode"));
class SearchPanel {
    static _panel;
    static show() {
        const column = vscode.window.activeTextEditor ? vscode.window.activeTextEditor.viewColumn : ViewColumn.One;
        SearchPanel._panel?.reveal(column);
        if (!SearchPanel._panel) {
            SearchPanel._panel = vscode.window.createWebviewPanel('searchPanel', 'Search Panel', { viewColumn: column, preserveFocus: true }, { enableScripts: true });
            SearchPanel._panel.webview.html = getWebviewContent();
            SearchPanel._panel.onDidDispose(() => { SearchPanel._panel = undefined; });
            SearchPanel._panel.webview.onDidReceiveMessage(message => {
                if (message.command === 'search') {
                    SearchPanel.handleSearch(message.text);
                }
            });
        }
    }
    static async handleSearch(query) {
        try {
            const response = await fetch('http://example.com/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });
            const data = await response.json();
            console.log(data); // 处理返回的数据
        }
        catch (error) {
            console.error(error);
        }
    }
}
exports.SearchPanel = SearchPanel;
function getWebviewContent() {
    const style = `
    <style>
      .search-box {
        width: 100%;
        padding: 10px;
      }
      input[type="text"] {
        width: 100%;
        height: 30px;
        padding: 5px;
        margin-bottom: 10px;
      }
      button {
        width: 100%;
        height: 30px;
        background-color: #007acc;
        color: white;
        border: none;
      }
    </style>
  `;
    const script = `
    <script>
      document.querySelector("button").addEventListener("click", function() {
        const text = document.querySelector("input").value;
        vscode.postMessage({ command: "search", text });
      });
    </script>
  `;
    return `<div class="search-box">
            <input type="text" placeholder="Search...">
            <button>Search</button>
          </div>${style}${script}`;
}
//# sourceMappingURL=searchPanel.js.map
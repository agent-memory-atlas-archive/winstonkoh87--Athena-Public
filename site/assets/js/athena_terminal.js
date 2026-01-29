/**
 * Athena Interactive Terminal
 * ===========================
 * Simulates a live session on the landing page
 */

const DEMO_SCRIPT = [
    { type: 'command', text: '/start', delay: 500 },
    { type: 'output', text: '⚡ ATHENA BOOT SEQUENCE', delay: 100 },
    { type: 'output', text: '🔄 Loading Core Identity...', delay: 300 },
    { type: 'output', text: '   ✓ Laws #0-#4 loaded', delay: 200 },
    { type: 'output', text: '   ✓ Bionic Stack initialized', delay: 200 },
    { type: 'output', text: '🔍 Priming Semantic Memory...', delay: 300 },
    { type: 'output', text: '   ✓ Vector database: 78MB indexed', delay: 200 },
    { type: 'output', text: '   ✓ GraphRAG: 1,460 communities', delay: 200 },
    { type: 'output', text: '', delay: 100 },
    { type: 'output', text: '✅ Ready. Session 862 started.', delay: 300 },
    { type: 'pause', delay: 1500 },
    { type: 'command', text: 'What was my decision on pricing strategy?', delay: 800 },
    { type: 'output', text: '', delay: 100 },
    { type: 'output', text: '🔍 Hybrid Search (RRF Fusion)...', delay: 300 },
    { type: 'output', text: '   Vector: 3 results (0.89, 0.82, 0.71)', delay: 200 },
    { type: 'output', text: '   Tags: #pricing #strategy found', delay: 200 },
    { type: 'output', text: '', delay: 100 },
    { type: 'output', text: '📋 From Session 847 (2026-01-15):', delay: 300 },
    { type: 'output', text: '   • Base rate: $100 minimum', delay: 200 },
    { type: 'output', text: '   • Scope reduction = price reduction', delay: 200 },
    { type: 'output', text: '   • Premium tier: 3x for urgency', delay: 200 },
    { type: 'output', text: '', delay: 100 },
    { type: 'output', text: '[Λ+35] Protocol 124 | Session 847', delay: 200 },
    { type: 'pause', delay: 2000 },
    { type: 'command', text: '/end', delay: 500 },
    { type: 'output', text: '', delay: 100 },
    { type: 'output', text: '💾 ATHENA SHUTDOWN', delay: 200 },
    { type: 'output', text: '📝 Session 862 logged', delay: 200 },
    { type: 'output', text: '✅ Insights captured. See you next time.', delay: 300 },
];

class AthenaTerminal {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) return;

        this.output = this.container.querySelector('.terminal-output');
        this.isRunning = false;
        this.currentIndex = 0;
    }

    async run() {
        if (this.isRunning || !this.output) return;
        this.isRunning = true;
        this.output.innerHTML = '';
        this.currentIndex = 0;

        for (const step of DEMO_SCRIPT) {
            await this.executeStep(step);
        }

        this.isRunning = false;

        // Loop after a pause
        setTimeout(() => this.run(), 5000);
    }

    async executeStep(step) {
        return new Promise(resolve => {
            setTimeout(() => {
                if (step.type === 'command') {
                    this.addLine(`<span class="prompt">&gt;</span> <span class="command">${step.text}</span>`);
                } else if (step.type === 'output') {
                    this.addLine(step.text);
                }
                // 'pause' type just waits
                resolve();
            }, step.delay);
        });
    }

    addLine(html) {
        const line = document.createElement('p');
        line.innerHTML = html;
        this.output.appendChild(line);
        this.output.scrollTop = this.output.scrollHeight;
    }
}

// Auto-start when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const terminal = new AthenaTerminal('athena-demo-terminal');
    if (terminal.container) {
        terminal.run();
    }
});

// 게임 상수
const GRID_WIDTH = 10;
const GRID_HEIGHT = 20;
const BLOCK_SIZE = 20;

// 테트리스 피스 정의
const PIECES = [
    { shape: [[1, 1, 1, 1]], color: '#00ffff' },           // I
    { shape: [[1, 1], [1, 1]], color: '#ffff00' },         // O
    { shape: [[0, 1, 0], [1, 1, 1]], color: '#ff00ff' },   // T
    { shape: [[1, 0, 0], [1, 1, 1]], color: '#0000ff' },   // L
    { shape: [[0, 0, 1], [1, 1, 1]], color: '#ff8800' },   // J
    { shape: [[0, 1, 1], [1, 1, 0]], color: '#00ff00' },   // S
    { shape: [[1, 1, 0], [0, 1, 1]], color: '#ff0000' }    // Z
];

// 게임 상태
class TetrisGame {
    constructor() {
        this.canvas = document.getElementById('tetrisCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.nextCanvas = document.getElementById('nextCanvas');
        this.nextCtx = this.nextCanvas.getContext('2d');
        
        this.grid = Array(GRID_HEIGHT).fill(null).map(() => Array(GRID_WIDTH).fill(0));
        this.score = 0;
        this.lines = 0;
        this.level = 1;
        this.gameOver = false;
        this.paused = false;
        
        this.currentPiece = this.createNewPiece();
        this.nextPiece = this.createNewPiece();
        this.currentX = Math.floor(GRID_WIDTH / 2) - 1;
        this.currentY = 0;
        
        this.dropSpeed = 1000 - (this.level - 1) * 100;
        this.lastDropTime = Date.now();
        
        this.setupControls();
        this.gameLoop();
    }

    createNewPiece() {
        const piece = PIECES[Math.floor(Math.random() * PIECES.length)];
        return {
            shape: piece.shape,
            color: piece.color
        };
    }

    setupControls() {
        document.addEventListener('keydown', (e) => {
            if (this.gameOver) return;
            
            switch(e.key) {
                case 'ArrowLeft':
                    this.movePiece(-1, 0);
                    e.preventDefault();
                    break;
                case 'ArrowRight':
                    this.movePiece(1, 0);
                    e.preventDefault();
                    break;
                case 'ArrowUp':
                    this.rotatePiece();
                    e.preventDefault();
                    break;
                case 'ArrowDown':
                    this.movePiece(0, 1);
                    e.preventDefault();
                    break;
                case ' ':
                    this.togglePause();
                    e.preventDefault();
                    break;
            }
        });
        
        document.getElementById('pauseBtn').addEventListener('click', () => this.togglePause());
        document.getElementById('restartBtn').addEventListener('click', () => location.reload());
    }

    movePiece(dx, dy) {
        if (this.paused || this.gameOver) return;
        
        this.currentX += dx;
        this.currentY += dy;
        
        if (this.isColliding()) {
            this.currentX -= dx;
            this.currentY -= dy;
            return false;
        }
        return true;
    }

    isColliding() {
        const piece = this.currentPiece.shape;
        
        for (let y = 0; y < piece.length; y++) {
            for (let x = 0; x < piece[y].length; x++) {
                if (piece[y][x] === 0) continue;
                
                const newX = this.currentX + x;
                const newY = this.currentY + y;
                
                if (newX < 0 || newX >= GRID_WIDTH || newY >= GRID_HEIGHT) {
                    return true;
                }
                
                if (newY >= 0 && this.grid[newY][newX] !== 0) {
                    return true;
                }
            }
        }
        return false;
    }

    rotatePiece() {
        if (this.paused || this.gameOver) return;
        
        const piece = this.currentPiece.shape;
        const rotated = this.rotatePieceArray(piece);
        
        const originalShape = this.currentPiece.shape;
        this.currentPiece.shape = rotated;
        
        if (this.isColliding()) {
            this.currentPiece.shape = originalShape;
        }
    }

    rotatePieceArray(array) {
        const rotated = [];
        for (let x = 0; x < array[0].length; x++) {
            const row = [];
            for (let y = array.length - 1; y >= 0; y--) {
                row.push(array[y][x]);
            }
            rotated.push(row);
        }
        return rotated;
    }

    lockPiece() {
        const piece = this.currentPiece.shape;
        
        for (let y = 0; y < piece.length; y++) {
            for (let x = 0; x < piece[y].length; x++) {
                if (piece[y][x] !== 0) {
                    const gridY = this.currentY + y;
                    const gridX = this.currentX + x;
                    
                    if (gridY >= 0) {
                        if (gridY < GRID_HEIGHT && gridX >= 0 && gridX < GRID_WIDTH) {
                            this.grid[gridY][gridX] = this.currentPiece.color;
                        }
                    } else {
                        this.endGame();
                        return;
                    }
                }
            }
        }
        
        this.clearLines();
        this.currentPiece = this.nextPiece;
        this.nextPiece = this.createNewPiece();
        this.currentX = Math.floor(GRID_WIDTH / 2) - 1;
        this.currentY = 0;
    }

    clearLines() {
        let clearedLines = 0;
        
        for (let y = GRID_HEIGHT - 1; y >= 0; y--) {
            if (this.grid[y].every(cell => cell !== 0)) {
                this.grid.splice(y, 1);
                this.grid.unshift(Array(GRID_WIDTH).fill(0));
                clearedLines++;
                y++;
            }
        }
        
        if (clearedLines > 0) {
            this.lines += clearedLines;
            this.score += clearedLines * clearedLines * 100;
            
            if (this.lines % 10 === 0) {
                this.level++;
                this.dropSpeed = Math.max(100, 1000 - (this.level - 1) * 100);
            }
            
            this.updateUI();
        }
    }

    updateUI() {
        document.getElementById('score').textContent = this.score;
        document.getElementById('lines').textContent = this.lines;
        document.getElementById('level').textContent = this.level;
    }

    togglePause() {
        if (this.gameOver) return;
        this.paused = !this.paused;
        document.getElementById('pauseBtn').textContent = this.paused ? '재개' : '일시정지';
    }

    endGame() {
        this.gameOver = true;
        document.getElementById('finalScore').textContent = this.score;
        document.getElementById('finalLines').textContent = this.lines;
        document.getElementById('gameOverModal').classList.add('show');
    }

    draw() {
        // 배경
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 그리드 선
        this.ctx.strokeStyle = '#333';
        this.ctx.lineWidth = 0.5;
        for (let i = 0; i <= GRID_WIDTH; i++) {
            this.ctx.beginPath();
            this.ctx.moveTo(i * BLOCK_SIZE, 0);
            this.ctx.lineTo(i * BLOCK_SIZE, this.canvas.height);
            this.ctx.stroke();
        }
        for (let i = 0; i <= GRID_HEIGHT; i++) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, i * BLOCK_SIZE);
            this.ctx.lineTo(this.canvas.width, i * BLOCK_SIZE);
            this.ctx.stroke();
        }
        
        // 격자에 있는 블록 그리기
        for (let y = 0; y < GRID_HEIGHT; y++) {
            for (let x = 0; x < GRID_WIDTH; x++) {
                if (this.grid[y][x] !== 0) {
                    this.ctx.fillStyle = this.grid[y][x];
                    this.ctx.fillRect(x * BLOCK_SIZE + 1, y * BLOCK_SIZE + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2);
                    this.ctx.strokeStyle = '#fff';
                    this.ctx.lineWidth = 1;
                    this.ctx.strokeRect(x * BLOCK_SIZE + 1, y * BLOCK_SIZE + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2);
                }
            }
        }
        
        // 현재 피스 그리기
        if (!this.paused) {
            const piece = this.currentPiece.shape;
            this.ctx.fillStyle = this.currentPiece.color;
            
            for (let y = 0; y < piece.length; y++) {
                for (let x = 0; x < piece[y].length; x++) {
                    if (piece[y][x] !== 0) {
                        const drawX = this.currentX + x;
                        const drawY = this.currentY + y;
                        
                        if (drawY >= 0) {
                            this.ctx.fillRect(drawX * BLOCK_SIZE + 1, drawY * BLOCK_SIZE + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2);
                            this.ctx.strokeStyle = '#fff';
                            this.ctx.lineWidth = 1;
                            this.ctx.strokeRect(drawX * BLOCK_SIZE + 1, drawY * BLOCK_SIZE + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2);
                        }
                    }
                }
            }
        }
        
        // 다음 피스 미리보기
        this.drawNextPiece();
    }

    drawNextPiece() {
        this.nextCtx.fillStyle = '#000';
        this.nextCtx.fillRect(0, 0, this.nextCanvas.width, this.nextCanvas.height);
        
        const piece = this.nextPiece.shape;
        const offsetX = (5 - piece[0].length) / 2;
        const offsetY = (5 - piece.length) / 2;
        
        this.nextCtx.fillStyle = this.nextPiece.color;
        for (let y = 0; y < piece.length; y++) {
            for (let x = 0; x < piece[y].length; x++) {
                if (piece[y][x] !== 0) {
                    const drawX = (offsetX + x) * 20;
                    const drawY = (offsetY + y) * 20;
                    this.nextCtx.fillRect(drawX + 1, drawY + 1, 18, 18);
                    this.nextCtx.strokeStyle = '#fff';
                    this.nextCtx.lineWidth = 1;
                    this.nextCtx.strokeRect(drawX + 1, drawY + 1, 18, 18);
                }
            }
        }
    }

    gameLoop() {
        const now = Date.now();
        
        if (!this.paused && !this.gameOver) {
            if (now - this.lastDropTime > this.dropSpeed) {
                if (!this.movePiece(0, 1)) {
                    this.lockPiece();
                }
                this.lastDropTime = now;
            }
        }
        
        this.draw();
        requestAnimationFrame(() => this.gameLoop());
    }
}

// 게임 시작
window.addEventListener('DOMContentLoaded', () => {
    new TetrisGame();
});

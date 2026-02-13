
        // Snake Game
        class Snake {
            constructor(x, y) {
                this.x = x;
                this.y = y;
            }
            
            move(direction) {
                console.log("Moving", direction);
            }
        }
        
        function createFood(x, y) {
            return { x, y, type: 'apple' };
        }
        
        const GAME_CONFIG = {
            width: 800,
            height: 600
        };
        
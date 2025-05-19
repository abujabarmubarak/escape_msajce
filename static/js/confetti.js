// Simple confetti animation
function startConfetti() {
    const confettiCount = 200;
    const confettiContainer = document.querySelector('.confetti-animation');
    
    // Create confetti pieces
    for (let i = 0; i < confettiCount; i++) {
        const confetti = document.createElement('div');
        confetti.classList.add('confetti-piece');
        
        // Randomize confetti properties
        const size = Math.random() * 10 + 5;
        const colorIndex = Math.floor(Math.random() * 4);
        const colors = ['#7c3aed', '#10b981', '#f59e0b', '#ef4444'];
        
        // Set confetti styles
        confetti.style.width = `${size}px`;
        confetti.style.height = `${size}px`;
        confetti.style.background = colors[colorIndex];
        confetti.style.left = `${Math.random() * 100}%`;
        confetti.style.top = `-${size}px`;
        confetti.style.opacity = Math.random() + 0.5;
        confetti.style.transform = `rotate(${Math.random() * 360}deg)`;
        
        // Set animation properties
        confetti.style.animationDuration = `${Math.random() * 3 + 2}s`;
        confetti.style.animationDelay = `${Math.random() * 5}s`;
        confetti.style.animationIterationCount = 'infinite';
        
        // Add to container
        confettiContainer.appendChild(confetti);
    }
    
    // Add confetti styles
    const style = document.createElement('style');
    style.textContent = `
        .confetti-animation {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
            overflow: hidden;
        }
        
        .confetti-piece {
            position: absolute;
            border-radius: 3px;
            animation: fall linear forwards;
        }
        
        @keyframes fall {
            0% {
                top: -10px;
                transform: translateX(0) rotate(0deg);
            }
            25% {
                transform: translateX(100px) rotate(90deg);
            }
            50% {
                transform: translateX(-100px) rotate(180deg);
            }
            75% {
                transform: translateX(50px) rotate(270deg);
            }
            100% {
                top: 100%;
                transform: translateX(-50px) rotate(360deg);
            }
        }
    `;
    document.head.appendChild(style);
}
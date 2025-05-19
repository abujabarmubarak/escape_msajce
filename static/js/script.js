// Flash Message Auto-dismiss
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.alert');
    
    flashMessages.forEach(message => {
        // Auto-dismiss flash messages after 5 seconds
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transition = 'opacity 0.5s ease';
            
            setTimeout(() => {
                message.remove();
            }, 500);
        }, 5000);
    });
    
    // Add animation to clue card if it exists
    const clueCard = document.querySelector('.clue-card');
    if (clueCard) {
        clueCard.classList.add('animate-in');
        
        // Add subtle glow effect to the clue text
        const clueText = document.querySelector('.clue-text');
        if (clueText) {
            setInterval(() => {
                clueText.classList.toggle('glow');
            }, 2000);
        }
    }
});

// Add CSS for animations
document.addEventListener('DOMContentLoaded', function() {
    const style = document.createElement('style');
    style.textContent = `
        .animate-in {
            animation: fadeIn 0.6s ease;
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .glow {
            box-shadow: 0 0 15px rgba(124, 58, 237, 0.5);
        }
    `;
    document.head.appendChild(style);
});
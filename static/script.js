document.addEventListener("DOMContentLoaded", function() {
    const container = document.querySelector('.container');
    container.style.opacity = '0';
    setTimeout(() => {
        container.style.transition = 'opacity 1s ease';
        container.style.opacity = '1';
    }, 100);
});

function createCodeParticle() {
    const particle = document.createElement('div');
    particle.className = 'code-particle';
    particle.style.left = Math.random() * window.innerWidth + 'px';
    
    // Random code symbols
    const symbols = ['{ }', '( )', '[ ]', '< >', ';', '// ', '= >', '++', '&&'];
    particle.textContent = symbols[Math.floor(Math.random() * symbols.length)];
    
    document.body.appendChild(particle);
    
    // Remove particle after animation
    particle.addEventListener('animationend', () => {
        document.body.removeChild(particle);
    });
}

function startLoadingAnimation() {
    const overlay = document.querySelector('.loading-overlay');
    const container = document.querySelector('.container');
    overlay.classList.add('show');
    container.classList.add('generating');
    
    // Create falling code particles
    const particleInterval = setInterval(() => {
        createCodeParticle();
    }, 200);
    
    return particleInterval;
}

function stopLoadingAnimation(particleInterval) {
    const overlay = document.querySelector('.loading-overlay');
    const container = document.querySelector('.container');
    overlay.classList.remove('show');
    container.classList.remove('generating');
    clearInterval(particleInterval);
}

function generateCode() {
    const language = document.getElementById("language").value;
    const question = document.getElementById("question").value;
    const output = document.getElementById("output");
    const button = document.querySelector('button');
    
    // Start loading animations
    const particleInterval = startLoadingAnimation();
    button.disabled = true;
    
    fetch("/generate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ question: question, language: language })
    })
    .then(response => response.json())
    .then(data => {
        // Stop loading animations
        stopLoadingAnimation(particleInterval);
        button.disabled = false;
        
        if (data.code && data.explanation) {  // Check for both code and explanation
            output.innerHTML = `
                <div class="code-section">
                    <h3>Code:</h3>
                    <button class="copy-btn" onclick="copyToClipboard(\`${data.code}\`)">
                        <i class="far fa-copy"></i> Copy Code
                    </button>
                    <pre><code>${data.code}</code></pre>
                </div>
                <div class="explanation-section">
                    <h3>Explanation:</h3>
                    <button class="copy-btn" onclick="copyToClipboard(\`${data.explanation}\`)">
                        <i class="far fa-copy"></i> Copy Explanation
                    </button>
                    <p>${data.explanation}</p>
                </div>
            `;

            // Add syntax highlighting animation
            const codeElement = output.querySelector('code');
            codeElement.classList.add('typing-animation');
            setTimeout(() => {
                codeElement.classList.remove('typing-animation');
            }, 1000);
        } else if (data.error) {
            output.innerHTML = `<span class="error">Error: ${data.error}</span>`;
        } else {
            output.innerHTML = `<span class="error">Error: Invalid response from server</span>`;
        }
    })
    .catch(error => {
        stopLoadingAnimation(particleInterval);
        button.disabled = false;
        output.innerHTML = '<span class="error">Error: Could not connect to server</span>';
        console.error('Error:', error);
    });
}

function selectRole(role) {
    const button = event.target;
    button.style.transform = 'scale(0.9)';
    
    setTimeout(() => {
        localStorage.setItem("userType", role);
        document.body.style.opacity = '0';
        setTimeout(() => {
            window.location.href = "/main";
        }, 500);
    }, 200);
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!');
    }).catch(err => {
        showToast('Failed to copy text');
        console.error('Copy failed:', err);
    });
}

function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 2000);
    }, 100);
}

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

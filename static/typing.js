        const text = document.querySelector(".second-text");
        const textArray = ["where friendships go to die", "enter at your own risk"];
        const startMessage = document.getElementById("start-message");
        let textIndex = 0;
        window.animationComplete = false;
        startMessage.style.display = "none";
        
        function typeText(texters, callback) {
            let charIndex = 0;
            const interval = setInterval(() =>{
                text.textContent = texters.slice(0,charIndex+1);
                charIndex++;
                if (charIndex === texters.length) {
                    clearInterval(interval);
                    setTimeout(callback,1000);
                }
            }, 100);
        }

        function deleteText(callback) {
            let charIndex = text.textContent.length;
            const interval = setInterval(() => {
                text.textContent = text.textContent.slice(0, charIndex -1);
                charIndex--;
                if (charIndex === 0) {
                    clearInterval(interval);
                    setTimeout(callback, 500);
                }
            }, 100);
        }

        function playAnimation() {
            if (textIndex >= textArray.length) {
                setTimeout(showStartMessage(), 1000);
                return;
            } 
            typeText(textArray[textIndex], () => {
                deleteText(() => {
                    textIndex++;
                    playAnimation(); 
                });
            });
        }

        function showStartMessage() {
            startMessage.style.display = "block";
            window.animationComplete = true
        }
        startMessage.style.display = "none";
        setTimeout(playAnimation, 3000);
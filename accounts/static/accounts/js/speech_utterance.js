// Check for browser support for speech synthesis and recognition
if ('webkitSpeechRecognition' in window) {
    const recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    // Function to speak a message
    function speakAIMessage(message, callback) {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(message);
            
            let voices = [];
            const setVoice = () => {
                voices = window.speechSynthesis.getVoices();
                const femaleVoice = voices.find(voice => voice.name.toLowerCase().includes('female'));
                if (femaleVoice) {
                    utterance.voice = femaleVoice;
                }
                
                utterance.volume = 1;
                utterance.pitch = 1.2;
                utterance.rate = 1.1;

                window.speechSynthesis.speak(utterance);

                // Start recognition after the speech ends
                utterance.onend = () => {
                    if (callback) callback();
                };
            };

            // Check if voices are already loaded
            if (window.speechSynthesis.getVoices().length !== 0) {
                setVoice();
            } else {
                window.speechSynthesis.onvoiceschanged = setVoice;
            }
        } else {
            console.error("Speech synthesis is not supported in this browser.");
        }
    }

    // Stop speech synthesis when navigating to another page
    window.addEventListener("beforeunload", () => {
        window.speechSynthesis.cancel();
    });

    document.getElementById("profileButton").addEventListener("click", function() {
        // Store an indicator in localStorage to trigger the profile greeting
        localStorage.setItem("speakProfileGreeting", "true");
        window.location.href = "basemenu.html";
    });

    // Speak a general welcome message and role-specific message every time the page loads
    window.onload = function() {
     //   if (!localStorage.getItem('hasSpokenWelcomeMessage')) {
            // Speak the general welcome message
            speakAIMessage("Welcome. to BCC Konnect", function() {
                // Store a flag in localStorage to indicate the message has been spoken
               // localStorage.setItem('hasSpokenWelcomeMessage', 'true');

            if (user_role === 'admin') {
                speakAIMessage("Welcome to the admin page", function() {
                    recognition.start(); 
                });
            } else if (user_role === 'teacher') {
                speakAIMessage("Welcome to the teacher page", function() {
                    recognition.start(); 
                });
            } else if (user_role === 'dean') {
                speakAIMessage("Welcome to the dean page", function() {
                    recognition.start(); 
                });
            } else if (user_role === 'student') {
                speakAIMessage("Welcome to the student page", function() {
                    recognition.start(); 
                });
            }
            
        });
  //  }
    };
} else {
    alert("Your browser does not support speech recognition. Try Chrome.");
} 

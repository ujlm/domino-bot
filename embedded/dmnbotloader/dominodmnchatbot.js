function injectCode(){
    var css = `<link rel="stylesheet" href="https://baleine.be/BCE/domino/dominodmnchatbot.css" />`;
    document.getElementsByTagName("head")[0].innerHTML += css;
    
    var chatbox = `
    <div class="chatbox dominobot">
    <div class="chatbox__support" id="chatbox_support">
        <div class="chatbox__header">
            <div class="chatbox__image--header">
                <img src="https://img.icons8.com/color/48/000000/circled-user-female-skin-type-5--v1.png" alt="image">
            </div>
            <div class="chatbox__content--header">
                <h4 class="chatbox__heading--header">Chat support</h4>
                <p class="chatbox__description--header">Hi. I'm your DMN chatbot. How can I help you?</p>
            </div>
        </div>
        <div class="chatbox__messages">
            <div></div>
        </div>
        <div class="chatbox__footer">
            <input type="text" placeholder="Write a message...">
            <button class="chatbox__send--footer send__button" id="send_btn">Send</button>
        </div>
    </div>
    <div class="chatbox__button" id="chatbox_btn">
        <button><img src="https://firebasestorage.googleapis.com/v0/b/dmnbot-2b8f9.appspot.com/o/dmnbot_assets%2Fchatbox-icon.svg?alt=media&token=babaae5d-de91-43fa-9ebd-2bdb99689ba1" /></button>
    </div>
</div>
    `;
    document.getElementsByTagName("body")[0].innerHTML += chatbox;
}
class Chatbox {
    constructor(apikey){
        this.args = {
            openButton: document.querySelector('.chatbot__button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button')
        }

        this.apikey = apikey;
        
        // Change host to ngrok url if running remotely
        this.host = "http://localhost:5000";
        //this.host = "https://d450-94-110-96-191.eu.ngrok.io";

        this.sessionId = Date.now().toString(36) + Math.random().toString(36).slice(2);
        console.log(`Session id: ${this.sessionId}`);
        this.init = true;
        this.state = false;
        this.messages = [];
        this.prevFooterContents = "";
    }
    
    display() {
        const {openButton, chatBox, sendButton} = this.args;

        document.getElementById('chatbox_btn').addEventListener('click', () => this.toggleState(chatBox));

        let chatbox = document.getElementById('chatbox_support');
        // Automatically send start message
        if(this.init){
            this.onSendButton(chatbox, "start");
            this.init = false;
        }

        chatbox.addEventListener("keyup", (event) => {
            if(event.key === "Enter" && event.target.tagName == "INPUT"){
                this.onSendButton(chatBox)
            }
        });
        const node = chatbox.querySelector('input');

        document.querySelector('body').addEventListener('click', (event) => {
            if(event.target.id === 'send_btn'){
                this.onSendButton(chatbox)
            }
            if (event.target.className === 'modelSelectBtn' && event.target.tagName == "BUTTON") {
                this.modelSelect(event.target.getAttribute('data-target').toString(), chatbox)
            }
            if(event.target.parentElement.className === 'modelSelectBtn' && event.target.parentElement.tagName == "BUTTON"){
                this.modelSelect(event.target.parentElement.getAttribute('data-target').toString(), chatbox)
            }
            if(event.target.classList.contains('link--back') || event.target.parentElement.classList.contains('link--back')){
                this.onSendButton(chatbox, "Back");
            }
            if(event.target.classList.contains('link--dontKnow') || event.target.parentElement.classList.contains('link--dontKnow')    ){
                this.onSendButton(chatbox, "I don't know")
            }
            if(event.target.classList.contains('link--explain') || event.target.parentElement.classList.contains('link--explain')){
                this.onSendButton(chatbox, "Why?");
            }
            if(event.target.classList.contains('link--whatIf') || event.target.parentElement.classList.contains('link--whatIf')){
                this.onSendButton(chatbox, "What if <property> were <value>?");
            }
            if(event.target.classList.contains('link--target') || event.target.parentElement.classList.contains('link--target')    ){
                this.setTarget(chatbox);
                //this.onSendButton(chatbox, "What should x be to alter y?");
            }
            if(event.target.id == "target__button__close" || event.target.parentElement.id == "target__button__close"){
                this.resetFooter();
            }
            if(event.target.classList.contains('link--showAllPaths') || event.target.parentElement.classList.contains('link--showAllPaths')    ){
                this.onSendButton(chatbox, "Show all paths")
                //this.onSendButton(chatbox, "What should x be to alter y?");
            }
            if(event.target.classList.contains('target--select--y')){
                console.log(event.target.value);
                this.getTargetOptions(event.target.value);
            }
            if(event.target.id === 'target__button'){
                console.log('Build target query');
                const t1 = "What should ";
                let t2 = document.querySelector('.target--select--x').value;
                const t3 = " be to alter ";
                let t4 = document.querySelector('.target--select--y').value;
                let query = t1 + " " + t2 + " " + t3 + " " + t4 + "?";
                console.log(query)
                this.onSendButton(chatbox, query);
                this.resetChatboxState();
            }
        });
    }

    toggleState(chatbox){
        this.state = !this.state;

        // Show/hide the chatbox
        if(this.state){
            chatbox.classList.add('chatbox--active')
        }else{
            chatbox.classList.remove('chatbox--active')
        }
    }
    
    scrollTo(hash) {
        location.hash = "#" + hash;
    }

    modelSelect(fileName, chatbox){
        console.log('Selected model: ', fileName);
        this.onSendButton(chatbox, fileName, true);
    }

    setTarget(){
        console.log('set target');
        this.prevFooterContents = document.querySelector('.chatbox__footer').innerHTML;
        document.querySelector('.chatbox__footer').innerHTML = "<div class='chatbot__optimization__builder'>What should <select name='target--select--x' class='target--select--x'><option value='y-not-set'>...</option></select> be to alter <select name='target--select--y' class='target--select--y'><option value='no-value'>loading...</option></select>?</div><button class='chatbox__send--footer send__button' id='target__button'>Send</button><button class='close__btn' id='target__button__close'>&#8592; Back to chat</button>";
        this.getTargetOptions();
    }
    
    resetFooter(){
        document.querySelector('.chatbox__footer').innerHTML = this.prevFooterContents;
    }

    resetChatboxState(){
        document.querySelector('.chatbox__footer').innerHTML = '<input type="text" placeholder="Write a message..."><button class="chatbox__send--footer send__button" id="send_btn">Send</button>';
    }

    onSendButton(chatbox, customText = undefined, hidden = false){
        var textField = chatbox.querySelector('input');
        textField.disabled = true;
        var text1 = ''
        var hidden = false;

        if(customText !== undefined){
            text1 = customText;
            //hidden = true; // Hide auto-generated messages
        }else{
            text1 = textField.value;
        }

        if(text1 === ""){
            return;
        }

        let msg1 = { name: "User", message: text1, hidden: hidden, apikey: this.apikey }
        this.messages.push(msg1);

        // Set loading message
        this.messages.push({ name: "DMNbot", message: `<div id="wave">
        <span class="srfriendzone"><span class="srname">Domino</span> is typing</span>
        <span class="dot one"></span>
        <span class="dot two"></span>
        <span class="dot three"></span>
        </div>`, apikey: this.apikey, hidden: false });
        if(textField !== null){textField.value = ''};
        this.updateChatText(chatbox);
        
        // Also add some catch of button clicks (dmn selection and others)
        fetch(this.host + '/predict', {
            method: 'POST',
            body: JSON.stringify({message: text1, apikey: this.apikey, sessionId: this.sessionId}),
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
        })
        .then(r => r.json())
        .then(r => {
            this.messages.pop();
            let msg2 = { name: "DMNbot", message: r.answer, apikey: this.apikey, hidden: false };
            this.messages.push(msg2);
            this.updateChatText(chatbox);
            textField.disabled = false;
            textField.focus();
        }).catch((error) => {
            console.error('Error: ', error);
            this.updateChatText(chatbox)
            if(textField !== null){textField.value = ''};
            textField.disabled = false;
        });
    }

    getTargetOptions(y = ''){
        // Also add some catch of button clicks (dmn selection and others)
        fetch(this.host + '/target', {
            method: 'POST',
            body: JSON.stringify({message: y, type: 'get-x', sessionId: this.sessionId}),
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
        })
        .then(r => r.json())
        .then(r => {
            console.log("Got options: " + r.options.x + r.options.y);
            // X options
            let optionsX = [];
            r.options.x.forEach(option => {
                optionsX.push("<option value='" + option + "'>" + option + "</option>");
            });
            document.querySelector('.target--select--x').innerHTML = optionsX;

            // Y options
            if(y == ''){
                let optionsY = [];
                r.options.y.forEach(option => {
                    optionsY.push("<option value='" + option + "'>" + option + "</option>");
                });
                document.querySelector('.target--select--y').innerHTML = optionsY;
            }
        }).catch((error) => {
            console.error('Error: ', error);
        });
    }

    updateChatText(chatbox, typing = false){
        var html = '';
        var hiddenClass = '';

        this.messages.slice().reverse().forEach((item) => {
            let lastMsg = 'msg-' + this.messages.indexOf(item);

            hiddenClass = '';
            if(item.hidden){
                hiddenClass = ' nodisp';
            }
            if(item.name === "DMNbot"){
                let controlBtns = '';
                let isGeneral, isOutcome, isTarget, isTargetOutcome, isQuestion = false;

                if(item.message.includes("How can I help you?") || item.message.includes("Are you sure you want to quit the model?")){
                    isGeneral = true;
                }

                /* TODO: not accurate for preformulated questions in annotations */
                if(item.message.includes("What is the value for")){
                    console.log("detected question");
                    isQuestion = true;
                }

                if(item.message.includes("What is the target value that you want to obtain for ")){
                    isTarget = true;
                }

                if(item.message.includes("In order for ") || item.message.includes("because of the following inputs") || item.message.includes("I'm sorry I cannot derive the value")){
                    isTargetOutcome = true;
                }

                if(item.message.includes("This is the final outcome")){
                    isOutcome = true;
                }

                if(!isGeneral && !isTarget){
                    if(!isTargetOutcome){
                        controlBtns = '<section class="link--bar"><a href="#" class="dmnbot--link link--back"><img src="https://s5.imgcdn.dev/BNhAh.png" alt="Go back" />Back</a>';
                    }else{
                        controlBtns = '<section class="link--bar">';
                    }
    
                    if(isOutcome && !item.message.includes("?")){
                        // Question: no explain, no target
                        controlBtns += '<a href="#" class="dmnbot--link link--explain"><img src="https://s5.imgcdn.dev/BN6NK.png" alt="Explain solution" />Explain</a>';
                    }
                    controlBtns += '</section>';
                }

                let helpMsg = '';
                
                if(isOutcome || (isTargetOutcome && !item.message.includes("In order for "))){
                    helpMsg += '<button class="modelSelectBtn dmnbot--link link--target"><span class="title">What should...?</span></button>';
                    helpMsg += '<a class="modelSelectBtn dmnbot--link link--whatIf" href="#"><span class="title">What if...?</span></a>';
                    helpMsg += '<a class="modelSelectBtn dmnbot--link link--showAllPaths" href="#"><span class="title">Show all paths</span></a>';
                }
                if(isQuestion){
                    helpMsg += '<br/><button class="modelSelectBtn dmnbot--link link--dontKnow"><span class="title">I don\'t know</span></button>';
                }
                
                
                html += '<div class="messages__item messages__item--visitor' + hiddenClass + '" id="' + lastMsg + '" >' + controlBtns + item.message + helpMsg + "</div>";
            }else{
                html += '<div class="messages__item messages__item--operator' + hiddenClass + '" id="' + lastMsg + '" >' + item.message + "</div>";
            }
        });

        const chatmessage = chatbox.querySelector('.chatbox__messages');
        chatmessage.innerHTML = html;

        this.scrollTo('msg-' + (parseInt(this.messages.length - 1)).toString());
    }
}

function initChatbox(apikey){
    injectCode();
    const chatbox = new Chatbox(apikey);
    window.onload = function(){
        console.log('dom loaded');
        chatbox.display();
    }
}
function formatTextAI(editor) {
    var content = editor.getContent();
    
    fetch('/format-text-ai/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({text: content}),
    })
    .then(response => response.json())
    .then(data => {
        editor.setContent(data.formatted_text);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

tinymce.init({
    selector: 'textarea',  // change this value according to your HTML
    // other TinyMCE options...
});
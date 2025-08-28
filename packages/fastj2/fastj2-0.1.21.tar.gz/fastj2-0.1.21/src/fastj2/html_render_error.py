render_error ="""
<html>
<head><title>Template Error</title></head>
<body>
    <h1>Template Rendering Error</h1>
    <p><strong>Template:</strong> {{ template_name }}</p>
    <p><strong>Error:</strong> {{ e }}</p>

    <h3>Context Information</h3>
    {{ context_info }}

    <details>
        <summary>Full Error Details</summary>
        <pre>{{ traceback }}</pre>
    </details>
</body>
</html>
""",
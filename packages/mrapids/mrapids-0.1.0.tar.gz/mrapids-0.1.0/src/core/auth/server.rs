use anyhow::{Context, Result};
use std::sync::mpsc::Sender;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpListener;
use url::Url;

/// Start a local HTTP server to receive OAuth callback
pub async fn start_callback_server(
    tx: Sender<String>,
    expected_state: String,
) -> Result<tokio::task::JoinHandle<()>> {
    let listener = TcpListener::bind("127.0.0.1:8899")
        .await
        .context("Failed to bind to port 8899. Is another instance running?")?;

    let handle = tokio::spawn(async move {
        if let Ok((mut stream, _)) = listener.accept().await {
            let mut buffer = vec![0; 4096];

            if let Ok(n) = stream.read(&mut buffer).await {
                let request = String::from_utf8_lossy(&buffer[..n]);

                // Parse the request line
                if let Some(request_line) = request.lines().next() {
                    let parts: Vec<&str> = request_line.split_whitespace().collect();
                    if parts.len() >= 2 {
                        let path = parts[1];

                        // Parse query parameters
                        if let Ok(url) = Url::parse(&format!("http://localhost{}", path)) {
                            let params: std::collections::HashMap<_, _> =
                                url.query_pairs().into_owned().collect();

                            // Check state parameter
                            if let Some(state) = params.get("state") {
                                if state == &expected_state {
                                    // Extract authorization code
                                    if let Some(code) = params.get("code") {
                                        let _ = tx.send(code.clone());

                                        // Send success response
                                        let response = build_success_response();
                                        let _ = stream.write_all(response.as_bytes()).await;
                                    } else if let Some(error) = params.get("error") {
                                        // Handle error response
                                        let error_desc = params
                                            .get("error_description")
                                            .map(|s| s.as_str())
                                            .unwrap_or("Unknown error");

                                        let response = build_error_response(error, error_desc);
                                        let _ = stream.write_all(response.as_bytes()).await;
                                    }
                                } else {
                                    // State mismatch - possible CSRF
                                    let response = build_error_response(
                                        "invalid_state",
                                        "State parameter mismatch",
                                    );
                                    let _ = stream.write_all(response.as_bytes()).await;
                                }
                            }
                        }
                    }
                }
            }
        }
    });

    Ok(handle)
}

/// Build success response HTML
fn build_success_response() -> String {
    let html = r#"<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Authentication Successful - MicroRapid</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            text-align: center;
            padding: 2rem;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }
        h1 {
            margin: 0 0 1rem 0;
            font-size: 2.5rem;
        }
        p {
            margin: 0.5rem 0;
            font-size: 1.2rem;
            opacity: 0.9;
        }
        .checkmark {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        .close-notice {
            margin-top: 2rem;
            font-size: 0.9rem;
            opacity: 0.7;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="checkmark">✅</div>
        <h1>Authentication Successful!</h1>
        <p>You have successfully authenticated with MicroRapid.</p>
        <p>You can now close this window and return to your terminal.</p>
        <p class="close-notice">This window will close automatically in 3 seconds...</p>
    </div>
    <script>
        setTimeout(() => window.close(), 3000);
    </script>
</body>
</html>"#;

    format!(
        "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {}\r\n\r\n{}",
        html.len(),
        html
    )
}

/// Build error response HTML
fn build_error_response(error: &str, description: &str) -> String {
    let html = format!(
        r#"<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Authentication Failed - MicroRapid</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
            color: white;
        }}
        .container {{
            text-align: center;
            padding: 2rem;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            max-width: 500px;
        }}
        h1 {{
            margin: 0 0 1rem 0;
            font-size: 2.5rem;
        }}
        p {{
            margin: 0.5rem 0;
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        .error {{
            font-size: 4rem;
            margin-bottom: 1rem;
        }}
        .error-details {{
            background: rgba(0, 0, 0, 0.2);
            padding: 1rem;
            border-radius: 5px;
            margin-top: 1rem;
            font-family: monospace;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="error">❌</div>
        <h1>Authentication Failed</h1>
        <p>The authentication process was not completed successfully.</p>
        <div class="error-details">
            <strong>Error:</strong> {}<br>
            <strong>Description:</strong> {}
        </div>
        <p style="margin-top: 2rem;">Please close this window and try again.</p>
    </div>
</body>
</html>"#,
        error, description
    );

    format!(
        "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {}\r\n\r\n{}",
        html.len(),
        html
    )
}

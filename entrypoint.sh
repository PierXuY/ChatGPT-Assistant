sed -i "1i\apiKey = $OPENAI_API_KEY" ./.streamlit/secrets.toml &
sed -i "s#^apiBase.*#apiBase = $OPENAI_API_BASE#" ./.streamlit/secrets.toml &
streamlit run app.py --server.port=8501 --server.enableCORS false --server.enableXsrfProtection false
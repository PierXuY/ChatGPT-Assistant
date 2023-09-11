if [ -n "$OPENAI_API_KEY" ]; then
    sed -i "1i\apikey = \"$OPENAI_API_KEY\"" ./.streamlit/secrets.toml
fi
if [ -n "$OPENAI_API_BASE" ]; then
    sed -i "s#^api_base.*#api_base = \"$OPENAI_API_BASE\"#" ./.streamlit/secrets.toml
fi
streamlit run app.py --server.port=8501 --server.enableCORS false --server.enableXsrfProtection false
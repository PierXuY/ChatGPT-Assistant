sed -i "1i\apikey = \"$OPENAI_API_KEY\"" ./.streamlit/secrets.toml &
sed -i "s#^api_base.*#api_base = \"$OPENAI_API_BASE\"#" ./.streamlit/secrets.toml &
streamlit run app.py --server.port=8501 --server.enableCORS false --server.enableXsrfProtection false

sed -i "s#^apiBase.*#api_base = \"$OPENAI_API_BASE\"#" ./.streamlit/secrets.toml
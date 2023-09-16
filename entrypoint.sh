if [ -n "$OPENAI_API_KEY" ]; then
    if grep -q "apikey" "./.streamlit/secrets.toml"; then
        sed -i "s#^apikey.*#apikey = \"$OPENAI_API_KEY\"#" ./.streamlit/secrets.toml
    else
        sed -i "1i\apikey = \"$OPENAI_API_KEY\"" ./.streamlit/secrets.toml
    fi
fi
if [ -n "$OPENAI_API_BASE" ]; then
    if grep -q "api_base" "./.streamlit/secrets.toml"; then
    sed -i "s#^api_base.*#api_base = \"$OPENAI_API_BASE\"#" ./.streamlit/secrets.toml
    else
        sed -i "1i\api_base = \"$OPENAI_API_BASE\"" ./.streamlit/secrets.toml
    fi
fi
streamlit run app.py --server.port=8501 --server.enableCORS false --server.enableXsrfProtection false
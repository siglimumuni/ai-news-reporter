# AI News Reporter Agent

This project implements an AI-powered news reporter agent that automatically:
1.  Fetches the latest global news using Google Gemini and its Search tool.
2.  Categorizes and summarizes news articles based on predefined topics.
3.  Generates a formatted HTML news digest email.
4.  Sends the email to configured recipients via the Gmail API.



## Features

*   **AI-Powered News Aggregation:** Uses Google Gemini (configurable model) with web search capabilities.
*   **Structured Output:** Leverages Gemini's JSON mode for reliable, structured news data based on Pydantic models.
*   **Categorized News:** Organizes news into configurable categories (e.g., Headlines, World Affairs, Economy, Tech, Canada, AI).
*   **HTML Email Generation:** Creates professionally formatted HTML emails using Jinja2 templates.

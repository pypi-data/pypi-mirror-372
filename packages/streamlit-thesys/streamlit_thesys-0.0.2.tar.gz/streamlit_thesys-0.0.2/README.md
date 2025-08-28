# streamlit-thesys

**Generative Visualizations in Streamlit, powered by [C1 by Thesys](https://thesys.dev).**

---

## What is `streamlit-thesys`?

`streamlit-thesys` is a Streamlit package that lets you generate **charts and visualizations** using **C1 by Thesys**.

Instead of manually coding every `st.pyplot` or `st.plotly_chart`, you can **describe the chart you want in plain language** and Thesys will create it in real time.

If you’ve ever asked:

- _“How do I generate charts from my data in Streamlit using AI?”_
- _“Can I create plots without writing matplotlib or plotly code?”_
- _“What’s the fastest way to connect Thesys with Streamlit for Generative Visualizations?”_

👉 This package is your answer.

---

## ⚡ Features

- **AI-generated charts** — bar, line, scatter, histogram, pie, and more.
- **Query-to-Chart** — describe your data question in text, get a chart back.
- **Seamless integration** with **C1 by Thesys**.
- **Works with your data** — Pandas DataFrames, CSVs, or APIs.
- **Exploratory analysis** — iterate on visualizations in seconds.

---

## 📦 Installation

```bash
pip install streamlit-thesys
```

---

## 🏁 Quickstart

```python
import streamlit as st
import pandas as pd
import streamlit_thesys as thesys

# Load some example data
df = pd.read_csv("sales.csv")
# Thesys API key can be generated at https://console.thesys.dev/
api_key = "<insert your api key here>"

st.title("Generative Visualizations with Thesys")

# Generate a chart dynamically
thesys.visualize(
  instructions="Show monthly sales as a line chart",
  data=df,
  api_key=api_key
)

# Try another
thesys.visualize(
  instructions="Plot top 5 products by revenue as a bar chart",
  data=df,
  api_key=api_key)
```

---

## 🎯 Why Use Thesys for Visualizations in Streamlit?

- **Speed:** No need to hand-code chart logic.
- **Flexibility:** Quickly try different chart types with natural language prompts.
- **Accessibility:** Anyone can generate charts — no matplotlib or plotly knowledge required.
- **Exploration:** Move faster when analyzing and presenting your data.

---

## ❓FAQ

**Q: Which visualization libraries does this use?**
This used the [Thesys C1 component](https://docs.thesys.dev/guides/embedding-c1-component) under the hood
which is based on other JS visualization libraries.

**Q: Can I use my own dataset?**
Yes — pass a Pandas DataFrame, CSV, or API response directly.

**Q: How is this different from coding charts in Streamlit manually?**
You don’t have to specify every chart property. Thesys interprets natural language and builds the chart for you.

**Q: Does it work with time series / categorical / numeric data?**
Yes. Thesys adapts the visualization type to the data you provide.

---

## 📚 Resources

- [Thesys Docs](https://docs.thesys.dev)
- [C1 by Thesys](https://thesys.dev)
- [Streamlit](https://streamlit.io)

---

## 🚀 Next Steps

- Explore the [examples](./examples) folder.
- Try prompts like:

  - “Compare revenue by region in a bar chart.”
  - “Plot customer growth over time as a line chart.”
  - “Show distribution of order sizes with a histogram.”

- Share your results with the [Thesys community](https://discord.gg/Pbv5PsqUSv).

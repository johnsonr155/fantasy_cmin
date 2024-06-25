import plotly.express as px


def get_treemap(df, path=["type", "policy_options"], length=20):
    def _add_breaks(text):
        words = text.split()
        lines = []
        line = ""

        for word in words:
            if len(line) + len(word) + 1 <= length:
                line = f"{line} {word}" if line else word
            else:
                lines.append(line)
                line = word

        lines.append(line)

        return "<br>".join(lines)

    df["policy_options"] = df["policy_options"].apply(_add_breaks)

    df.loc[df["flag"] == "scalable", "scalable_text"] = (
        "<i>(" + df["option"].str.title() + ")</i>"
    )
    df.loc[df["flag"] != "scalable", "scalable_text"] = ""

    df["policy_options"] = (
        "<b>€"
        + df["cost"].apply(lambda x: round(x, 1)).astype(str)
        + "mn</b> "
        + df["scalable_text"]
        + "<br>"
        + df["policy_options"]
    )

    fig = px.treemap(
        df,
        path=path,
        values="cost",
    )

    fig.update_layout(margin=dict(t=0, b=0, l=0, r=20))

    return fig

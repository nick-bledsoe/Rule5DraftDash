"""Styling utilities for dataframe display."""

import pandas as pd


def apply_gradient_styling(df: pd.DataFrame, player_type: str) -> pd.DataFrame:
    """Apply gradient color styling to AAA stats based on performance percentiles."""

    def get_color_from_percentile(value, col_min, col_max, reverse=False):
        """Generate color based on percentile within the column range."""
        if pd.isna(value) or col_min == col_max:
            return ''

        # Calculate percentile (0-1)
        percentile = (value - col_min) / (col_max - col_min)

        if reverse:  # For stats where lower is better
            percentile = 1 - percentile

        # Color gradient from red -> yellow -> green
        if percentile < 0.5:
            # Red to Yellow (bottom 50%)
            r = 255
            g = int(255 * (percentile * 2))
            b = 0
        else:
            # Yellow to Green (top 50%)
            r = int(255 * (2 - percentile * 2))
            g = 255
            b = 0

        # Adjust for dark theme - make colors less intense
        r = int(r * 0.7)
        g = int(g * 0.7)
        b = int(b * 0.7)

        return f'background-color: rgb({r},{g},{b}); color: white; font-weight: bold'

    if player_type == "Hitter":
        # Stats where higher is better
        higher_better = ["xBA", "xwOBA", "xSLG", "Barrel%", "EV", "BB%", "Sprint Speed"]
        # Stats where lower is better
        lower_better = ["Chase%", "K%"]

        def style_hitter(row):
            styles = [''] * len(row)

            for col in higher_better:
                if col in row.index and pd.notna(row[col]):
                    col_data = df[col].dropna()
                    if len(col_data) > 1:
                        idx = row.index.get_loc(col)
                        styles[idx] = get_color_from_percentile(
                            row[col], col_data.min(), col_data.max(), reverse=False
                        )

            for col in lower_better:
                if col in row.index and pd.notna(row[col]):
                    col_data = df[col].dropna()
                    if len(col_data) > 1:
                        idx = row.index.get_loc(col)
                        styles[idx] = get_color_from_percentile(
                            row[col], col_data.min(), col_data.max(), reverse=True
                        )

            return styles

        return df.style.apply(style_hitter, axis=1)

    else:  # Pitcher
        # Stats where higher is better
        higher_better = ["Max Velo", "K%", "Whiff%", "Chase%"]
        # Stats where lower is better
        lower_better = ["xBA", "xwOBA", "xSLG", "BB%"]

        def style_pitcher(row):
            styles = [''] * len(row)

            for col in higher_better:
                if col in row.index and pd.notna(row[col]):
                    col_data = df[col].dropna()
                    if len(col_data) > 1:
                        idx = row.index.get_loc(col)
                        styles[idx] = get_color_from_percentile(
                            row[col], col_data.min(), col_data.max(), reverse=False
                        )

            for col in lower_better:
                if col in row.index and pd.notna(row[col]):
                    col_data = df[col].dropna()
                    if len(col_data) > 1:
                        idx = row.index.get_loc(col)
                        styles[idx] = get_color_from_percentile(
                            row[col], col_data.min(), col_data.max(), reverse=True
                        )

            return styles

        return df.style.apply(style_pitcher, axis=1)
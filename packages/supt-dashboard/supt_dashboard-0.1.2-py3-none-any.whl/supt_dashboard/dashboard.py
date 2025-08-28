import numpy as np
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

def stress(phi, C=1, D=100):
    return -C * (1 - np.exp(-D * (phi - 0.5)**2))

# Sample demo data
sample_noaa = {
    "time_tag": ["2025-09-01T00:00:00Z", "2025-09-02T00:00:00Z", "2025-09-03T00:00:00Z"],
    "speed": [400, 520, 700]
}
sample_usgs = {
    "features": [
        {"properties": {"time": 1756700000000, "mag": 2.2}},
        {"properties": {"time": 1756786400000, "mag": 1.6}},
        {"properties": {"time": 1756872800000, "mag": 3.1}}
    ]
}

def noaa_to_delta_phi(noaa_json):
    times = pd.to_datetime(noaa_json["time_tag"]).tz_localize(None)
    speeds = noaa_json["speed"]
    delta_phi = [0.5 - (s/2000) for s in speeds]
    return pd.DataFrame({"time": times, "delta_phi": delta_phi})

def usgs_to_delta_phi(usgs_json):
    times = pd.to_datetime([f["properties"]["time"] for f in usgs_json["features"]], unit="ms").tz_localize(None)
    mags = [f["properties"]["mag"] for f in usgs_json["features"]]
    delta_phi = [0.5 - (m/10) for m in mags]
    return pd.DataFrame({"time": times, "delta_phi": delta_phi})

df_noaa = noaa_to_delta_phi(sample_noaa)
df_usgs = usgs_to_delta_phi(sample_usgs)
df = pd.concat([df_noaa, df_usgs]).sort_values("time")
df["stress"] = df["delta_phi"].apply(stress)

def build_dashboard(dataframe):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=dataframe["time"], y=dataframe["delta_phi"], mode="lines+markers", name="ΔΦ Drift", line=dict(color="orange")), secondary_y=False)
    fig.add_trace(go.Scatter(x=dataframe["time"], y=dataframe["stress"], mode="lines+markers", name="Stress k(ΔΦ)", line=dict(color="red")), secondary_y=True)
    fig.add_hline(y=-1.0, line=dict(color="black", dash="dash"), annotation_text="ZFCM Threshold", secondary_y=True)
    fig.update_layout(title="SUPT ψ-Fold Dashboard (Demo: NOAA + USGS Stubs)", xaxis_title="Date", yaxis_title="ΔΦ Drift", yaxis2_title="Stress", template="plotly_white")
    return fig

def get_dashboard_html():
    fig = build_dashboard(df)
    return fig.to_html(full_html=True, include_plotlyjs="cdn")

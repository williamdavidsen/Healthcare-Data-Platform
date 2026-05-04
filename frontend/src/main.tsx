import React from "react";
import ReactDOM from "react-dom/client";
import {
  Activity,
  BarChart3,
  ChevronDown,
  ChevronsUpDown,
  CircleDollarSign,
  Database,
  FileCheck2,
  Gauge,
  HeartPulse,
  LineChart,
  MapPinned,
  Menu,
  ShieldCheck,
  Sparkles,
  Stethoscope,
  X,
  TrendingUp,
  Trophy,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart as RechartsLineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import "./styles.css";

type SummaryRow = {
  country: string;
  iso_code: string;
  year: number;
  life_expectancy: number;
  diabetes_prevalence: number;
  obesity_rate: number;
  health_spending_per_capita: number;
  gdp_per_capita: number;
  health_risk_score: number;
  country_risk_index?: number;
};

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8002";

const metrics = [
  { key: "life_expectancy", label: "Life expectancy", unit: "years", color: "#005eb8" },
  { key: "diabetes_prevalence", label: "Diabetes", unit: "%", color: "#b0005a" },
  { key: "obesity_rate", label: "Obesity", unit: "%", color: "#007c89" },
  { key: "health_spending_per_capita", label: "Spending", unit: "USD", color: "#6b4eff" },
  { key: "health_risk_score", label: "Risk score", unit: "score", color: "#d2421f" },
] as const;

type MetricKey = (typeof metrics)[number]["key"];
type SortKey = "country" | "life_expectancy" | "diabetes_prevalence" | "health_risk_score";
type SortDirection = "asc" | "desc";

type FreshnessReport = {
  latest_year: number;
  earliest_year: number;
  row_count: number;
  country_count: number;
  latest_country_count: number;
  uses_carried_forward_values: boolean;
};

type QualityReport = {
  passed: boolean;
  row_count: number;
  country_count: number;
  year_min: number;
  year_max: number;
  duplicate_country_year_rows: number;
  missing_values: Record<string, number>;
};

type Insight = {
  title: string;
  country: string;
  year: number;
  value: number;
  unit: string;
};

function formatNumber(value: number, unit?: string) {
  const formatted = new Intl.NumberFormat("en", {
    maximumFractionDigits: value > 100 ? 0 : 1,
  }).format(value);
  return unit ? `${formatted} ${unit}` : formatted;
}

function App() {
  const [summary, setSummary] = React.useState<SummaryRow[]>([]);
  const [countries, setCountries] = React.useState<string[]>([]);
  const [country, setCountry] = React.useState("");
  const [trend, setTrend] = React.useState<SummaryRow[]>([]);
  const [metric, setMetric] = React.useState<MetricKey>("life_expectancy");
  const [freshness, setFreshness] = React.useState<FreshnessReport | null>(null);
  const [quality, setQuality] = React.useState<QualityReport | null>(null);
  const [insights, setInsights] = React.useState<Insight[]>([]);
  const [menuOpen, setMenuOpen] = React.useState(false);
  const [tableSort, setTableSort] = React.useState<{
    key: SortKey;
    direction: SortDirection;
  }>({ key: "life_expectancy", direction: "desc" });
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState("");

  React.useEffect(() => {
    async function loadInitialData() {
      try {
        const [summaryResponse, countriesResponse, freshnessResponse, qualityResponse, insightsResponse] =
          await Promise.all([
            fetch(`${API_BASE}/summary`),
            fetch(`${API_BASE}/countries`),
            fetch(`${API_BASE}/freshness`),
            fetch(`${API_BASE}/quality`),
            fetch(`${API_BASE}/insights`),
          ]);

        if (
          !summaryResponse.ok ||
          !countriesResponse.ok ||
          !freshnessResponse.ok ||
          !qualityResponse.ok ||
          !insightsResponse.ok
        ) {
          throw new Error("Could not load health indicators");
        }

        const summaryData = (await summaryResponse.json()) as SummaryRow[];
        const countryData = (await countriesResponse.json()) as string[];
        setSummary(summaryData);
        setCountries(countryData);
        setCountry(countryData[0] ?? "");
        setFreshness((await freshnessResponse.json()) as FreshnessReport);
        setQuality((await qualityResponse.json()) as QualityReport);
        setInsights((await insightsResponse.json()) as Insight[]);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    }

    loadInitialData();
  }, []);

  React.useEffect(() => {
    if (!country) {
      return;
    }

    async function loadTrend() {
      try {
        const response = await fetch(`${API_BASE}/trend?country=${encodeURIComponent(country)}`);
        if (!response.ok) {
          throw new Error("Could not load country trend");
        }
        setTrend((await response.json()) as SummaryRow[]);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      }
    }

    loadTrend();
  }, [country]);

  const selectedMetric = metrics.find((item) => item.key === metric) ?? metrics[0];
  const selectedCountry = summary.find((row) => row.country === country);
  const latestYear = summary[0]?.year ?? new Date().getFullYear();
  const avgLifeExpectancy =
    summary.reduce((total, row) => total + row.life_expectancy, 0) / Math.max(summary.length, 1);
  const lowestRisk = [...summary].sort((a, b) => a.health_risk_score - b.health_risk_score)[0];
  const sortedSummary = React.useMemo(() => {
    return [...summary].sort((a, b) => {
      const modifier = tableSort.direction === "asc" ? 1 : -1;
      if (tableSort.key === "country") {
        return a.country.localeCompare(b.country) * modifier;
      }
      return (a[tableSort.key] - b[tableSort.key]) * modifier;
    });
  }, [summary, tableSort]);

  function updateTableSort(key: SortKey) {
    setTableSort((current) => ({
      key,
      direction: current.key === key && current.direction === "desc" ? "asc" : "desc",
    }));
  }

  if (loading) {
    return (
      <main className="shell center-state">
        <div className="loader" aria-label="Loading" />
      </main>
    );
  }

  return (
    <main className="shell">
      <header className="topbar" aria-label="Application header">
        <a className="brand" href="/">
          <span className="brand-mark" aria-hidden="true">
            <HeartPulse size={27} strokeWidth={2.2} />
          </span>
          <span>
            <strong>Healthcare Data</strong>
            <small>Public health indicators</small>
          </span>
        </a>
        <button
          className="menu-toggle"
          type="button"
          aria-expanded={menuOpen}
          aria-controls="primary-navigation"
          aria-label={menuOpen ? "Close navigation menu" : "Open navigation menu"}
          onClick={() => setMenuOpen((open) => !open)}
        >
          {menuOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
        <nav
          className={`nav-links ${menuOpen ? "open" : ""}`}
          id="primary-navigation"
          aria-label="Primary navigation"
        >
          <a href="#overview" onClick={() => setMenuOpen(false)}>
            Overview
          </a>
          <a href="#trend" onClick={() => setMenuOpen(false)}>
            Trend
          </a>
          <a href="#countries" onClick={() => setMenuOpen(false)}>
            Countries
          </a>
        </nav>
      </header>

      <section className="hero" id="overview">
        <div className="hero-copy">
          <div className="hero-title-card">
            <span className="eyebrow">
              <ShieldCheck size={18} /> Validated analytics dataset
            </span>
            <h1>Understand country health trends at a glance.</h1>
          </div>
          <div className="hero-summary-card">
            <span className="card-icon" aria-hidden="true">
              <Sparkles size={22} />
            </span>
            <div>
              <h2>Quick comparison</h2>
              <p>
                Compare life expectancy, diabetes, obesity, health spending and
                GDP across public health datasets.
              </p>
              <div className="hero-actions">
                <a className="primary-action" href="#trend">
                  Explore trends
                  <LineChart size={19} />
                </a>
              </div>
            </div>
          </div>
        </div>
        <div className="hero-side">
          <div className="hero-info-card">
            <span className="card-icon" aria-hidden="true">
              <TrendingUp size={22} />
            </span>
            <div>
              <h2>How to use this view</h2>
              <p>
                See the newest country-level health data, choose a country, and
                compare how key indicators change over time.
              </p>
              <ul>
                <li>Spot long-term changes in life expectancy and risk factors.</li>
                <li>Compare countries with the nearest published values for the current year.</li>
              </ul>
            </div>
          </div>
          <div className="hero-panel" aria-label="Key project status">
            <div>
              <span className="panel-icon" aria-hidden="true">
                <Database size={20} />
              </span>
              <p>
                <span>Dataset year</span>
                <strong>{latestYear}</strong>
              </p>
            </div>
            <div>
              <span className="panel-icon" aria-hidden="true">
                <MapPinned size={20} />
              </span>
              <p>
                <span>Countries</span>
                <strong>{countries.length}</strong>
              </p>
            </div>
            <div>
              <span className="panel-icon" aria-hidden="true">
                <Trophy size={20} />
              </span>
              <p>
                <span>Best risk profile</span>
                <strong>{lowestRisk?.country ?? "N/A"}</strong>
              </p>
            </div>
          </div>
        </div>
      </section>

      {error ? <p className="error-state">{error}</p> : null}

      <section className="stat-grid" aria-label="Headline metrics">
        <MetricCard
          icon={<Stethoscope />}
          label="Average life expectancy"
          value={formatNumber(avgLifeExpectancy, "years")}
          detail="Latest dataset average"
        />
        <MetricCard
          icon={<Activity />}
          label="Selected country"
          value={selectedCountry?.country ?? country}
          detail={selectedCountry ? `${selectedCountry.iso_code} / ${selectedCountry.year}` : ""}
        />
        <MetricCard
          icon={<CircleDollarSign />}
          label="Health spending"
          value={
            selectedCountry
              ? formatNumber(selectedCountry.health_spending_per_capita, "USD")
              : "N/A"
          }
          detail="Per person"
        />
      </section>

      <section className="insight-grid" aria-label="Advanced analytics insights">
        <article className="quality-card">
          <span className="metric-icon" aria-hidden="true">
            <FileCheck2 />
          </span>
          <div>
            <p>Data quality</p>
            <strong>{quality?.passed ? "Passed" : "Needs review"}</strong>
            <small>
              {quality
                ? `${quality.row_count} rows, ${quality.duplicate_country_year_rows} duplicates`
                : "Loading report"}
            </small>
          </div>
        </article>
        <article className="quality-card">
          <span className="metric-icon" aria-hidden="true">
            <Database />
          </span>
          <div>
            <p>Freshness</p>
            <strong>{freshness?.latest_year ?? latestYear}</strong>
            <small>
              {freshness
                ? `${freshness.latest_country_count} countries with nearest current values`
                : "Loading freshness"}
            </small>
          </div>
        </article>
        {insights.slice(0, 3).map((insight) => (
          <article className="quality-card" key={`${insight.title}-${insight.country}`}>
            <span className="metric-icon" aria-hidden="true">
              <Gauge />
            </span>
            <div>
              <p>{insight.title}</p>
              <strong>{insight.country}</strong>
              <small>
                {formatNumber(insight.value, insight.unit)} / {insight.year}
              </small>
            </div>
          </article>
        ))}
      </section>

      <section className="workspace" id="trend">
        <aside className="control-panel" aria-label="Dashboard filters">
          <label>
            <span>Country</span>
            <select value={country} onChange={(event) => setCountry(event.target.value)}>
              {countries.map((item) => (
                <option key={item}>{item}</option>
              ))}
            </select>
            <ChevronDown className="select-icon" size={20} aria-hidden="true" />
          </label>

          <div className="metric-picker" role="group" aria-label="Metric selector">
            {metrics.map((item) => (
              <button
                key={item.key}
                className={metric === item.key ? "active" : ""}
                onClick={() => setMetric(item.key)}
                type="button"
              >
                {item.label}
              </button>
            ))}
          </div>
        </aside>

        <section className="chart-panel">
          <div className="section-heading chart-heading">
            <div>
              <span className="context-pill">{country}</span>
              <h2>
                <LineChart size={22} />
                {selectedMetric.label} trend
              </h2>
            </div>
            <p>{selectedMetric.unit}</p>
          </div>
          <div className="chart-frame">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsLineChart data={trend} margin={{ left: 0, right: 20, top: 20, bottom: 8 }}>
                <CartesianGrid stroke="#d6e4f2" strokeDasharray="4 4" />
                <XAxis dataKey="year" tickLine={false} axisLine={false} />
                <YAxis tickLine={false} axisLine={false} width={70} />
                <Tooltip contentStyle={{ borderRadius: 6, borderColor: "#b8cee3" }} />
                <Line
                  type="monotone"
                  dataKey={metric}
                  stroke={selectedMetric.color}
                  strokeWidth={3}
                  dot={{ r: 5, fill: selectedMetric.color }}
                />
              </RechartsLineChart>
            </ResponsiveContainer>
          </div>
        </section>
      </section>

      <section className="country-section" id="countries">
        <div className="section-heading chart-heading">
          <div>
            <span className="context-pill">Latest comparison</span>
            <h2>
              <BarChart3 size={22} />
              Country overview
            </h2>
          </div>
          <p>{latestYear}</p>
        </div>
        <div className="compare-grid">
          <div className="chart-frame compact">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={summary} margin={{ left: 0, right: 10, top: 18, bottom: 8 }}>
                <CartesianGrid stroke="#d6e4f2" strokeDasharray="4 4" vertical={false} />
                <XAxis
                  dataKey="country"
                  tickLine={false}
                  axisLine={false}
                  interval="preserveStartEnd"
                  minTickGap={28}
                />
                <YAxis tickLine={false} axisLine={false} width={70} />
                <Tooltip contentStyle={{ borderRadius: 6, borderColor: "#b8cee3" }} />
                <Bar dataKey="life_expectancy" fill="#005eb8" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <SortableHeader
                    active={tableSort.key === "country"}
                    direction={tableSort.direction}
                    label="Country"
                    onClick={() => updateTableSort("country")}
                  />
                  <SortableHeader
                    active={tableSort.key === "life_expectancy"}
                    direction={tableSort.direction}
                    label="Life"
                    onClick={() => updateTableSort("life_expectancy")}
                  />
                  <SortableHeader
                    active={tableSort.key === "diabetes_prevalence"}
                    direction={tableSort.direction}
                    label="Diabetes"
                    onClick={() => updateTableSort("diabetes_prevalence")}
                  />
                  <SortableHeader
                    active={tableSort.key === "health_risk_score"}
                    direction={tableSort.direction}
                    label="Risk"
                    onClick={() => updateTableSort("health_risk_score")}
                  />
                </tr>
              </thead>
              <tbody>
                {sortedSummary.map((row) => (
                  <tr key={row.iso_code}>
                    <td>{row.country}</td>
                    <td>{formatNumber(row.life_expectancy)}</td>
                    <td>{formatNumber(row.diabetes_prevalence, "%")}</td>
                    <td>{formatNumber(row.health_risk_score)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </main>
  );
}

function SortableHeader({
  active,
  direction,
  label,
  onClick,
}: {
  active: boolean;
  direction: SortDirection;
  label: string;
  onClick: () => void;
}) {
  return (
    <th>
      <button
        className={`sort-button ${active ? "active" : ""}`}
        type="button"
        onClick={onClick}
        aria-sort={active ? (direction === "asc" ? "ascending" : "descending") : "none"}
      >
        {label}
        <ChevronsUpDown size={16} />
      </button>
    </th>
  );
}

function MetricCard({
  icon,
  label,
  value,
  detail,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  detail?: string;
}) {
  return (
    <article className="metric-card">
      <span className="metric-icon" aria-hidden="true">
        {icon}
      </span>
      <div>
        <p>{label}</p>
        <strong>{value}</strong>
        {detail ? <small>{detail}</small> : null}
      </div>
    </article>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

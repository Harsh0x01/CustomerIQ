import React from "react";
import { AlertTriangle, RotateCcw } from "lucide-react";

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error("CustomerIQ render failure", error, info);
  }

  reset = () => {
    this.setState({ error: null });
  };

  render() {
    if (!this.state.error) {
      return this.props.children;
    }

    return (
      <div className="flex min-h-screen items-center justify-center bg-void px-6">
        <section className="glass-panel max-w-xl rounded-lg p-6 shadow-cyan">
          <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg border border-danger/40 bg-danger/10 text-danger">
            <AlertTriangle size={20} aria-hidden="true" />
          </div>
          <h1 className="text-xl font-semibold text-ink">Interface fault detected</h1>
          <p className="mt-3 text-sm leading-6 text-muted">
            {this.state.error.message || "A dashboard module failed to render."}
          </p>
          <button
            type="button"
            onClick={this.reset}
            className="focus-ring mt-5 inline-flex items-center gap-2 rounded-lg border border-cyan/40 bg-cyan/10 px-4 py-2 text-sm font-medium text-cyan transition hover:bg-cyan/15"
          >
            <RotateCcw size={16} aria-hidden="true" />
            Retry
          </button>
        </section>
      </div>
    );
  }
}

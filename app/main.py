from fastapi import FastAPI

app = FastAPI(
    title="AegisEval",
    description="A production-grade AI evaluation and benchmarking platform.",
    version="0.1.0",
)


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Welcome to AegisEval 🚀"}


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
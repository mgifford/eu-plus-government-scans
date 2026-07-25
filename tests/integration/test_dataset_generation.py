import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from src.cli.generate_relationship_dataset import write_json, main


def test_write_json_determinism():
    data = {
        "z": 1,
        "a": [3, 2, 1],
        "m": {"b": 2, "a": 1}
    }
    
    with TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "test.json"
        write_json(out, data, minify=True)
        
        with out.open("r") as f:
            content = f.read()
            
        # Should be minified and sorted by key
        assert content == '{"a":[3,2,1],"m":{"a":1,"b":2},"z":1}'

def test_dataset_generation_pipeline(monkeypatch):
    """Test the overall orchestrator script execution."""
    with TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        toon_dir = base / "toon"
        rel_dir = base / "rels"
        out_dir = base / "out"
        
        toon_dir.mkdir()
        rel_dir.mkdir()
        
        # Write fake TOON
        (toon_dir / "iceland.toon").write_text(json.dumps({
            "country": "Iceland",
            "domains": [{"canonical_domain": "reykjavik.is"}]
        }))
        
        # Write fake rels
        (rel_dir / "scan.jsonl").write_text(json.dumps({
            "source_domain": "reykjavik.is",
            "target_domain": "stjornarradid.is",
            "target_hostname": "www.stjornarradid.is",
            "relationship_type": "editorial_link",
            "source_pages": 5,
            "observations": 10,
            "first_seen": "2026-07-15T00:00:00Z",
            "last_seen": "2026-07-15T00:00:00Z"
        }) + "\n")
        
        class DummyArgs:
            def __init__(self):
                self.toon_dir = toon_dir
                self.relationships_dir = rel_dir
                self.out_dir = out_dir
                self.sh_commit = "HEAD"
                self.minify = True
            
        monkeypatch.setattr("argparse.ArgumentParser.parse_args", lambda self: DummyArgs())
        
        # Mock SoftwareHeritageFetcher so it doesn't do a real HTTP request
        class MockFetcher:
            def __init__(self, *args, **kwargs): pass
            async def fetch_and_cache(self, *args, **kwargs): return Path("dummy.csv")
            def parse_dataset(self, path): return {}
            
        monkeypatch.setattr("src.cli.generate_relationship_dataset.SoftwareHeritageFetcher", MockFetcher)
        
        main()
        
        assert out_dir.exists()
        assert (out_dir / "manifest.json").exists()
        assert (out_dir / "global" / "summary.json").exists()
        
        is_dir = out_dir / "countries" / "ICELAND"
        if not is_dir.exists():
            dirs = list((out_dir / "countries").glob("*"))
            pytest.fail(f"ICELAND dir not found. Found: {dirs}")
        assert is_dir.exists()
        assert (is_dir / "nodes.json").exists()
        assert (is_dir / "editorial-edges.json").exists()
        
        with (is_dir / "nodes.json").open("r") as f:
            nodes = json.load(f)
            assert any(n["domain"] == "reykjavik.is" for n in nodes)

            reykjavik = next(n for n in nodes if n["domain"] == "reykjavik.is")
            assert reykjavik["classification_status"] == "confirmed"
            assert "curated_source" in reykjavik["classification_basis"]
            
        with (is_dir / "editorial-edges.json").open("r") as f:
            edges = json.load(f)
            assert len(edges) == 1
            assert edges[0]["target"] == "stjornarradid.is"

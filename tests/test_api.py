import importlib
import os

from fastapi.testclient import TestClient


def client(tmp_path):
    os.environ["MISCALE_DB"] = str(tmp_path / "test.db")
    os.environ["MISCALE_SCANNER"] = "off"
    import app.main as main
    importlib.reload(main)
    return TestClient(main.app, headers={"Accept-Language": "en"}), main


def test_profiles_measurements_and_settings(tmp_path):
    c, main = client(tmp_path)
    with c:
        assert c.get("/api/ping").json() == {"ok": True}
        p = c.post("/api/profiles", json={"name": "Alex", "height_cm": 178, "birth": "1990-01-01", "male": True}).json()
        mid = main.db.insert({"measured_at": "2026-10-12T07:30:00", "weight_kg": 80, "impedance": 500,
                              "profile_id": None, "metrics": {}})
        m = c.patch(f"/api/measurements/{mid}", json={"profile_id": p["id"]}).json()
        assert m["profile_id"] == p["id"] and m["metrics"]["body_fat"] > 0
        assert c.put("/api/settings", json={"unit": "lb"}).json()["unit"] == "lb"
        assert c.put("/api/settings", json={"unit": "stone"}).status_code == 422
        r = c.put(f"/api/profiles/{p['id']}/photo", content=b"\xff\xd8fake", headers={"content-type": "image/jpeg"})
        assert r.status_code == 200 and c.get(f"/api/profiles/{p['id']}/photo").content == b"\xff\xd8fake"
        bad = c.put(f"/api/profiles/{p['id']}/photo", content=b"x", headers={"content-type": "text/plain"})
        assert bad.status_code == 415
        c.delete(f"/api/profiles/{p['id']}")
        assert c.get("/api/measurements").json()[0]["profile_id"] is None


def test_websocket_status(tmp_path):
    c, _ = client(tmp_path)
    with c, c.websocket_connect("/ws") as ws:
        assert ws.receive_json() == {"type": "status", "scanner": False, "scanner_error": None, "last_seen": None}


def test_pwa_files(tmp_path):
    c, _ = client(tmp_path)
    with c:
        m = c.get("/manifest.webmanifest")
        assert m.headers["content-type"].startswith("application/manifest+json")
        assert {i["purpose"] for i in m.json()["icons"]} == {"any", "maskable"}
        for icon in m.json()["icons"]:
            assert c.get(icon["src"]).status_code == 200
        assert c.get("/sw.js").headers["content-type"].startswith("text/javascript")
        assert c.get("/favicon.ico").status_code == 200


def test_chinese_errors_through_api(tmp_path):
    c, _ = client(tmp_path)
    c.headers["Accept-Language"] = "zh-CN"
    with c:
        p = c.post("/api/profiles", json={"name": "小明"}).json()
        bad_photo = c.put(f"/api/profiles/{p['id']}/photo", content=b"x",
                          headers={"content-type": "text/plain"})
        assert bad_photo.status_code == 415
        assert bad_photo.json()["detail"] == "请上传 JPEG、PNG 或 WebP 格式的图片。"
        bad_profile = c.post("/api/profiles", json={"name": "", "height_cm": 300})
        assert bad_profile.status_code == 422
        assert "姓名" in str(bad_profile.json()["detail"])
        assert "身高" in str(bad_profile.json()["detail"])
        missing = c.put("/api/profiles/999", json={"name": "小明"})
        assert missing.status_code == 404 and missing.json()["detail"] == "未找到请求的内容。"

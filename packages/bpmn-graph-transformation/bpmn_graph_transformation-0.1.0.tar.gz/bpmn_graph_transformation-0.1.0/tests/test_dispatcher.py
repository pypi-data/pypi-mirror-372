import os
import json
from pathlib import Path
from unittest.mock import patch, mock_open


from bpmn_mp.dispatcher import dispatch_parse

# Lokasi file sample BPMN
CURRENT_DIR = Path(__file__).parent
BPMN_FILE = CURRENT_DIR / "samples" / "MyDiagram1.bpmn"
OUTPUT_FILE = CURRENT_DIR / "samples" / "output_Dispatcher.json"

def test_dispatch_bpmn_and_save_output():
    """
    Memastikan dispatch_parse dapat memproses file BPMN,
    mengembalikan data yang valid, dan menyimpan output.
    """
    assert BPMN_FILE.exists(), f"❌ File tidak ditemukan: {BPMN_FILE}"

    try:
        # Jalankan fungsi dispatcher dengan file BPMN asli
        result, result_type = dispatch_parse(BPMN_FILE)

        # Memastikan hasil parsing adalah dictionary
        assert isinstance(result, dict), "❌ Output bukan dictionary"
        
        # Memastikan tipe file yang dikembalikan benar
        assert result_type == "bpmn", f"❌ Tipe yang dikembalikan salah: {result_type}"
        
        # Contoh validasi konten dasar (sesuaikan dengan isi file Anda)
        assert "flowElements" in result, "❌ 'flowElements' tidak ditemukan"
        assert isinstance(result["flowElements"], list), "❌ 'flowElements' bukan list"

        print("✅ File .bpmn berhasil diparse oleh dispatcher!")
        
        # Simpan hasil ke file output
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"📁 Output disimpan di: {OUTPUT_FILE}")

    except Exception as e:
        print("❌ Terjadi error saat menjalankan pengujian:")
        print(e)
        assert False, str(e)

# pytest tests/test_dispatcher.py -s

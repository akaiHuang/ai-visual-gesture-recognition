#!/usr/bin/env python3
"""
Matplotlib 字型快取生成工具

用途: 預先建立 Matplotlib 字型快取,避免首次啟動時的掃描延遲

使用方法:
1. 在乾淨環境執行此腳本生成快取
2. 將生成的 fontlist-*.json 複製到專案的 mpl-cache/ 資料夾
3. 修改 config.py 讓 MPLCONFIGDIR 指向專案內的 mpl-cache/
"""

import matplotlib as mpl
from matplotlib import font_manager as fm
import shutil
import os
from pathlib import Path

def build_font_cache():
    """建立 Matplotlib 字型快取"""
    print("=" * 60)
    print("📦 Matplotlib 字型快取生成工具")
    print("=" * 60)
    
    # 顯示版本資訊
    print(f"\n✅ Matplotlib 版本: {mpl.__version__}")
    original_cache_dir = mpl.get_cachedir()
    print(f"✅ 預設快取目錄: {original_cache_dir}")
    
    # 觸發重建字型快取
    print("\n🔨 正在重建字型快取...")
    print("   (這會掃描系統所有字型,可能需要 10-30 秒)")
    
    # Matplotlib 3.x 使用 FontManager 來觸發快取建立
    try:
        # 方法 1: 直接訪問 FontManager 觸發初始化
        _ = fm.fontManager
        # 方法 2: 明確重建 (較舊版本)
        if hasattr(fm, '_rebuild'):
            fm._rebuild()
        # 方法 3: 新版本 API
        elif hasattr(fm.FontManager, '__call__'):
            fm.FontManager()
    except Exception as e:
        print(f"   ⚠️  警告: {e}")
        # 後備方案: 只是訪問 findfont 也會觸發快取
        _ = fm.findfont(fm.FontProperties())
    
    print("✅ 字型快取重建完成!")
    
    # 列出生成的快取檔案
    print(f"\n📂 快取檔案位置: {original_cache_dir}")
    cache_path = Path(original_cache_dir)
    if cache_path.exists():
        fontlist_files = list(cache_path.glob("fontlist-*.json"))
        if fontlist_files:
            for f in fontlist_files:
                size_kb = f.stat().st_size / 1024
                print(f"   ✅ {f.name} ({size_kb:.1f} KB)")
        else:
            print("   ⚠️  未找到 fontlist-*.json 檔案")
    
    # 複製到專案目錄
    project_cache_dir = Path(__file__).parent / "mpl-cache"
    project_cache_dir.mkdir(exist_ok=True)
    
    print(f"\n📋 複製快取到專案: {project_cache_dir}")
    copied_count = 0
    
    # 複製所有 fontlist 和 tex 相關檔案
    for pattern in ["fontlist-*.json", "*.cache", "tex.cache"]:
        for src_file in cache_path.glob(pattern):
            dst_file = project_cache_dir / src_file.name
            shutil.copy2(src_file, dst_file)
            print(f"   ✅ {src_file.name}")
            copied_count += 1
    
    if copied_count == 0:
        print("   ⚠️  沒有檔案可複製")
    else:
        print(f"\n✅ 成功複製 {copied_count} 個檔案!")
    
    # 生成使用說明
    readme_path = project_cache_dir / "README.md"
    readme_content = f"""# Matplotlib 字型快取

此目錄包含預先建立的 Matplotlib 字型快取檔案。

## 資訊

- **Matplotlib 版本**: {mpl.__version__}
- **生成日期**: {Path(__file__).stat().st_mtime}
- **原始快取位置**: {original_cache_dir}

## 用途

這些快取檔案用於加速 Matplotlib 初始化，避免首次啟動時掃描系統字型的延遲。

## 更新

如果 Matplotlib 版本更新或系統字型改變，請重新執行:

```bash
python build_mpl_font_cache.py
```

## 檔案列表

{chr(10).join(f"- `{f.name}` ({f.stat().st_size / 1024:.1f} KB)" for f in project_cache_dir.glob("*") if f.is_file() and f.name != "README.md")}
"""
    
    readme_path.write_text(readme_content, encoding='utf-8')
    print(f"\n📝 已生成說明文件: {readme_path}")
    
    # 提示下一步
    print("\n" + "=" * 60)
    print("✅ 完成! 下一步:")
    print("=" * 60)
    print(f"1. 快取檔案已複製到: {project_cache_dir}")
    print("2. config.py 已設定使用此快取目錄")
    print("3. 重新啟動應用程式以測試效果")
    print("\n💡 提示: 首次啟動應該會快很多!")
    print("=" * 60)

if __name__ == "__main__":
    build_font_cache()

import asyncio
import sys
import httpx
from pyglow.pyglow import Glow


def print_banner():
    Glow.prints(r"""
         _ __    _   _    __ _  __   __   __ _ 
        | '_ \  | | | |  / _` | \ \ / /  / _` |
        | |_) | | |_| | | (_| |  \ V /  | (_| |
        | .__/   \__, |  \__,_|   \_/    \__,_|
        |_|      |___/                         
                """, "Bold hex(#108DE6)")
    Glow.print("[Bold hex(#108DE6)][link=https://pypi.org/project/pyava]pyava[/][/] is a command line tool to help you check the availability of a package name you want on [link=https://pypi.org]PyPI[/]\n")
    Glow.print("[Bold hex(#108DE6)]Version:[/] 1.2.0")
    Glow.print("[Bold hex(#108DE6)]GitHub:[/] [link=https://github.com/BirukBelihu/pyava]pyava[/]")
    Glow.print("[Bold hex(#108DE6)]License:[/] [link=https://github.com/birukbelihu/pyava/blob/master/LICENSE]Apache License 2.0[/]")
    Glow.print(f"[Bold hex(#108DE6)]Author:[/] [link=https://github.com/BirukBelihu]BirukBelihu[/]")
    sys.exit(0)


async def check_package_name(client: httpx.AsyncClient, package_name: str, timeout: float):
    pypi_api_url = f"https://pypi.org/pypi/{package_name}/json"

    try:
        request = await client.get(pypi_api_url, timeout=timeout)

        if request.status_code == 200:
            response = request.json()
            package_info = response.get("info", {})
            releases = response.get("releases", {})
            urls = response.get("urls", [])

            latest_version = package_info.get("version", "Not Specified")
            release_date = None
            if latest_version in releases and releases[latest_version]:
                release_date = releases[latest_version][0].get("upload_time")

            files = []
            for file in urls:
                files.append({
                    "filename": file.get("filename"),
                    "python_version": file.get("python_version"),
                    "size_kb": round(file.get("size", 0) / 1024, 2)
                })

            return {
                "package_name": package_name,
                "is_available": False,
                "summary": package_info.get("summary"),
                "version": latest_version,
                "author": package_info.get("author"),
                "author_email": package_info.get("author_email"),
                "home_page": package_info.get("home_page"),
                "license": package_info.get("license"),
                "requires_python": package_info.get("requires_python"),
                "keywords": package_info.get("keywords"),
                "project_urls": package_info.get("project_urls"),
                "release_date": release_date,
                "files": files
            }
        else:
            return {"package_name": package_name, "is_available": True}
    except Exception as exception:
        return {"package_name": package_name, "error": str(exception)}


async def run_package_name_checker(package_names, timeout, silent=False):
    async with httpx.AsyncClient() as client:
        tasks = [check_package_name(client, package_name, timeout) for package_name in package_names]
        results = await asyncio.gather(*tasks)

        for result in results:
            if "error" in result:
                if not silent:
                    Glow.prints(
                        f"⚠️  Could not check `{result['package_name']}` due to: {result['error']}",
                        "Bold Red"
                    )
                continue

            if result.get("is_available"):
                print_status(result['package_name'], True)
            else:
                print_status(result['package_name'], False)
                if not silent:
                    print_full_metadata(result)


def print_status(package_name, is_available):
    if is_available:
        Glow.prints(f"✅ {package_name} is available", "Bold Green")
    else:
        Glow.prints(f"❌ {package_name} is already taken", "Red")


def print_full_metadata(result):
    Glow.print(f"[Bold Yellow]=== 📦 About {result['package_name']} ===[/]")

    if result.get("summary"):
        Glow.print(f"[Green]Summary:[/] {result.get('summary')}")
    else:
        Glow.print("[Green]Summary:[/] [Yellow]Not Specified[/]")

    if result.get("version"):
        Glow.print(f"[Green]Version:[/] {result.get('version')}")
    else:
        Glow.print("[Green]Version:[/] [Yellow]Not Specified[/]")

    if result.get("author"):
        Glow.print(f"[Green]Author:[/] {result.get('author')}")
    else:
        Glow.print("[Green]Author:[/] [Yellow]Not Specified[/]")

    if result.get("author_email"):
        Glow.print(f"[Green]Author Email:[/] {result.get('author_email')}")
    else:
        Glow.print("[Green]Author Email:[/] [Yellow]Not Specified[/]")

    if result.get("home_page"):
        Glow.print(f"[Green]Home Page:[/] {result.get('home_page')}")
    else:
        Glow.print("[Green]Home Page:[/] [Yellow]Not Specified[/]")

    if result.get("license"):
        Glow.print(f"[Green]License:[/] {result.get('license')}")
    else:
        Glow.print("[Green]License:[/] [Yellow]Not Specified[/]")

    if result.get("requires_python"):
        Glow.print(f"[Green]Requires Python:[/] {result['requires_python']}")
    else:
        Glow.print("[Green]Requires Python:[/] [Yellow]Not Specified[/]")

    if result.get("keywords"):
        Glow.print(f"[Green]Keywords:[/] {result['keywords']}")
    else:
        Glow.print("[Green]Keywords:[/] [Yellow]Not Specified[/]")

    if result.get("project_urls"):
        Glow.print("[Green]Project URLs:[/]")
        for key, value in result["project_urls"].items():
            Glow.print(f"   • {key}: {value}")

    if result.get("release_date"):
        Glow.print(f"[Green]Latest Release Date:[/] {result['release_date']}")

    if result.get("files"):
        Glow.print(f"[Green]Available Files:[/]")
        for file in result["files"]:
            Glow.print(f"   • {file['filename']} ({file['size_kb']} KB, {file['python_version']})")

    Glow.prints("=" * 60 + "\n", "Blue Italic")

"""Create the PharmaGenie Kaggle demo video with narrated audio."""

from __future__ import annotations

import html
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "demo_video"
SCREENSHOT_DIR = ROOT / "docs" / "screenshots"
WIDTH = 1920
HEIGHT = 1080
FPS = 30


@dataclass(frozen=True)
class Scene:
    title: str
    subtitle: str
    bullets: list[str]
    narration: str
    screenshot: str | None = None
    accent: tuple[int, int, int] = (70, 220, 255)


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    font_dir = Path("C:/Windows/Fonts")
    for candidate in (
        font_dir / ("segoeuib.ttf" if bold else "segoeui.ttf"),
        font_dir / ("arialbd.ttf" if bold else "arial.ttf"),
    ):
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


FONT_TITLE = load_font(74, bold=True)
FONT_SUBTITLE = load_font(34)
FONT_SECTION = load_font(30, bold=True)
FONT_BODY = load_font(27)
FONT_SMALL = load_font(21)


def rounded_rect(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill: tuple[int, int, int],
    outline: tuple[int, int, int] | None = None,
) -> None:
    draw.rounded_rectangle(box, radius=28, fill=fill, outline=outline, width=2)


def draw_background(draw: ImageDraw.ImageDraw, accent: tuple[int, int, int]) -> None:
    for y in range(HEIGHT):
        t = y / HEIGHT
        draw.line([(0, y), (WIDTH, y)], fill=(int(6 + 12 * t), int(13 + 18 * t), int(26 + 34 * t)))

    grid_color = (24, 74, 96)
    for x in range(0, WIDTH, 96):
        draw.line([(x, 0), (x, HEIGHT)], fill=grid_color, width=1)
    for y in range(0, HEIGHT, 96):
        draw.line([(0, y), (WIDTH, y)], fill=grid_color, width=1)

    for i in range(16):
        x = 120 + i * 112
        y = 120 + ((i * 73) % 760)
        draw.ellipse((x, y, x + 5, y + 5), fill=accent)

    for offset in range(0, 900, 120):
        draw.arc(
            (WIDTH - 640 - offset // 5, -220 + offset, WIDTH + 180, 660 + offset),
            start=210,
            end=330,
            fill=(accent[0] // 2, accent[1] // 2, accent[2] // 2),
            width=2,
        )


def draw_header(draw: ImageDraw.ImageDraw, scene: Scene) -> None:
    draw.text((72, 54), "PharmaGenie", fill=(235, 250, 255), font=FONT_TITLE)
    draw.text((76, 137), "AI Multi-Agent Drug Discovery Workbench", fill=(155, 238, 255), font=FONT_SUBTITLE)
    draw.line((76, 190, 655, 190), fill=scene.accent, width=4)


def wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        current = ""
        for word in words:
            trial = f"{current} {word}".strip()
            if draw.textbbox((0, 0), trial, font=font)[2] <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


def draw_bullets(draw: ImageDraw.ImageDraw, x: int, y: int, bullets: list[str], max_width: int) -> int:
    for bullet in bullets:
        draw.ellipse((x, y + 10, x + 12, y + 22), fill=(100, 245, 210))
        for line in wrap(draw, bullet, FONT_BODY, max_width):
            draw.text((x + 34, y), line, fill=(223, 241, 246), font=FONT_BODY)
            y += 38
        y += 20
    return y


def paste_screenshot(base: Image.Image, screenshot_name: str, box: tuple[int, int, int, int]) -> None:
    shot = Image.open(SCREENSHOT_DIR / screenshot_name).convert("RGB")
    target_w = box[2] - box[0]
    target_h = box[3] - box[1]
    shot.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
    frame = Image.new("RGB", (target_w, target_h), (13, 22, 36))
    frame.paste(shot, ((target_w - shot.width) // 2, (target_h - shot.height) // 2))
    border = ImageDraw.Draw(frame)
    border.rounded_rectangle((0, 0, target_w - 1, target_h - 1), radius=26, outline=(90, 230, 255), width=3)
    base.paste(frame, (box[0], box[1]))


def draw_architecture(draw: ImageDraw.ImageDraw, x: int, y: int, accent: tuple[int, int, int]) -> None:
    boxes = [
        ("Streamlit UI", x, y),
        ("FastAPI", x + 390, y),
        ("Coordinator", x + 780, y),
        ("Planner", x + 780, y + 190),
        ("ADK Agents", x + 390, y + 380),
        ("MCP Tools", x + 780, y + 380),
        ("PubMed | UniProt | PubChem | Trials", x, y + 570),
        ("Gemini 2.5 Flash synthesis", x + 780, y + 570),
    ]
    for label, bx, by in boxes:
        rounded_rect(draw, (bx, by, bx + 310, by + 96), fill=(10, 34, 52), outline=accent)
        draw.text((bx + 24, by + 28), label, fill=(238, 252, 255), font=FONT_SECTION)

    for start, end in [
        ((x + 310, y + 48), (x + 390, y + 48)),
        ((x + 700, y + 48), (x + 780, y + 48)),
        ((x + 935, y + 96), (x + 935, y + 190)),
        ((x + 780, y + 238), (x + 700, y + 428)),
        ((x + 700, y + 428), (x + 780, y + 428)),
        ((x + 935, y + 476), (x + 935, y + 570)),
        ((x + 310, y + 618), (x + 780, y + 428)),
    ]:
        draw.line((start, end), fill=(120, 245, 220), width=4)
        draw.ellipse((end[0] - 6, end[1] - 6, end[0] + 6, end[1] + 6), fill=(120, 245, 220))


def render_scene(scene: Scene, index: int) -> Path:
    image = Image.new("RGB", (WIDTH, HEIGHT), (7, 14, 25))
    draw = ImageDraw.Draw(image)
    draw_background(draw, scene.accent)
    draw_header(draw, scene)

    draw.text((76, 235), scene.title, fill=(255, 255, 255), font=FONT_TITLE)
    for i, line in enumerate(wrap(draw, scene.subtitle, FONT_SUBTITLE, 900)):
        draw.text((80, 324 + i * 44), line, fill=(178, 211, 222), font=FONT_SUBTITLE)

    if scene.screenshot:
        draw_bullets(draw, 88, 430, scene.bullets, 650)
        paste_screenshot(image, scene.screenshot, (820, 250, 1818, 960))
    elif "architecture" in scene.title.lower():
        draw_bullets(draw, 88, 430, scene.bullets, 600)
        draw_architecture(draw, 650, 315, scene.accent)
    else:
        rounded_rect(draw, (82, 430, 1838, 920), fill=(9, 28, 44), outline=(45, 128, 155))
        draw_bullets(draw, 126, 486, scene.bullets, 1600)

    draw.text(
        (76, 1006),
        "Kaggle Capstone | Agents for Good | Google ADK + MCP + Gemini",
        fill=(140, 180, 194),
        font=FONT_SMALL,
    )
    path = OUT_DIR / "frames" / f"scene_{index:02d}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    return path


def generate_tts(text: str, output: Path) -> None:
    escaped = html.escape(text, quote=True)
    script = f"""
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SelectVoice('Microsoft Zira Desktop')
$synth.Rate = 0
$synth.Volume = 100
$synth.SetOutputToWaveFile('{output}')
$synth.Speak('{escaped}')
$synth.Dispose()
"""
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script], check=True, cwd=ROOT)


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / float(wav.getframerate())


def create_scene_video(ffmpeg: str, image_path: Path, audio_path: Path, output_path: Path) -> None:
    duration = max(wav_duration(audio_path) + 0.35, 3.0)
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-loop",
            "1",
            "-framerate",
            str(FPS),
            "-i",
            str(image_path),
            "-i",
            str(audio_path),
            "-t",
            f"{duration:.2f}",
            "-vf",
            "scale=1920:1080,format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-shortest",
            str(output_path),
        ],
        check=True,
    )


def concatenate(ffmpeg: str, clips: list[Path], output: Path) -> None:
    concat_file = OUT_DIR / "concat.txt"
    concat_file.write_text("\n".join(f"file '{clip.as_posix()}'" for clip in clips), encoding="utf-8")
    subprocess.run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(output)], check=True)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "audio").mkdir(exist_ok=True)
    (OUT_DIR / "clips").mkdir(exist_ok=True)

    scenes = [
        Scene(
            title="Architecture first",
            subtitle="Google ADK multi-agent system for evidence-grounded early drug discovery hypotheses.",
            bullets=[
                "Streamlit collects disease and research goal inputs and visualizes agent progress.",
                "FastAPI exposes health, research, and discovery endpoints for demos and deployment.",
                "ADK agents coordinate planning, literature, protein, compound, clinical trial, ranking, and reporting work.",
                "MCP-style tools connect agents to PubMed, UniProt, PubChem, ClinicalTrials.gov, and report generation.",
            ],
            narration="First, the architecture. PharmaGenie is an AI driven biomedical discovery workbench. The Streamlit interface sends a disease and research goal to FastAPI. A coordinator and planner route the task across Google ADK agents. Those agents call MCP style tools for PubMed, UniProt, PubChem, Clinical Trials dot gov, and report generation. Gemini synthesizes the evidence into ranked, validation ready hypotheses.",
        ),
        Scene(
            title="Codebase walkthrough",
            subtitle="Modular agents, secure services, tests, documentation, and deployment assets.",
            bullets=[
                "app/agent.py defines the ADK root agent and sub-agent graph.",
                "src/pharmagenie/agents contains independently testable domain agents.",
                "src/pharmagenie/mcp_servers exposes tool functions and MCP server entry points.",
                "src/pharmagenie/sources contains source clients with graceful fallbacks.",
                "tests, Docker, GitHub Actions, and docs support the Kaggle submission story.",
            ],
            narration="Next, the codebase. The app folder contains the Google ADK entry point with the root agent. The agents package keeps each biomedical role modular and independently testable. MCP server modules expose the tool layer. Source clients handle PubMed, UniProt, PubChem, and Clinical Trials. The project also includes tests, Docker, GitHub Actions, documentation, screenshots, and Kaggle deliverables.",
            accent=(120, 245, 210),
        ),
        Scene(
            title="End-to-end demo input",
            subtitle="Researchers begin with a disease area and a specific research objective.",
            bullets=[
                "The UI asks for the disease and discovery goal directly on the first screen.",
                "Preset examples make it fast to demonstrate oncology, neurology, or rare disease workflows.",
                "The interface uses a science-fiction console style while keeping the workflow practical.",
            ],
            narration="Now the end to end demo. The researcher starts in the Streamlit interface, enters a disease, and describes the research goal. The goal can be target discovery, candidate prioritization, or evidence synthesis. Preset examples help during the five minute presentation, but the same screen accepts custom biomedical questions.",
            screenshot="01-streamlit-input-console.png",
            accent=(90, 205, 255),
        ),
        Scene(
            title="Agents executing live",
            subtitle="The UI shows the multi-agent workflow progressing instead of hiding the pipeline.",
            bullets=[
                "Coordinator validates the request and starts the run.",
                "Planner decomposes the task across specialized agents.",
                "Literature, Protein, Compound, Clinical Trial, Ranking, and Report agents run as visible stages.",
            ],
            narration="When the run starts, the app shows the agent swarm in motion. The coordinator validates the request. The planner decomposes it. Literature, protein, compound, clinical trial, evidence ranking, and report agents execute as visible stages, so judges can see that this is an agentic workflow and not a single hidden prompt.",
            screenshot="02-agent-swarm-running.png",
            accent=(180, 135, 255),
        ),
        Scene(
            title="Discovery hypotheses",
            subtitle="A ranked dossier of target and compound hypotheses with evidence and risk notes.",
            bullets=[
                "Outputs are framed as in-silico hypotheses requiring lab validation.",
                "Evidence ranking combines literature, target biology, compound data, and trial context.",
                "Markdown and PDF downloads make the final dossier shareable.",
            ],
            narration="The result is a research dossier, not a medical recommendation. PharmaGenie ranks target and compound hypotheses, explains the supporting evidence, and flags limitations. The output is designed for early stage research triage, with markdown and PDF download options for sharing the dossier.",
            screenshot="03-discovery-hypotheses.png",
            accent=(100, 245, 210),
        ),
        Scene(
            title="Backend and deployability",
            subtitle="FastAPI, Docker, and Cloud Run compatible settings make the system easy to review.",
            bullets=[
                "The FastAPI docs expose /health, /research, and /discover.",
                "Environment variables keep secrets out of the codebase.",
                "Docker and docker-compose support repeatable local and cloud execution.",
            ],
            narration="The backend is also demo ready. FastAPI exposes health, research, and discovery endpoints through interactive docs. Secrets are loaded from environment variables. Docker and docker compose make the app portable, and the structure is compatible with a Cloud Run deployment story.",
            screenshot="04-fastapi-docs.png",
            accent=(255, 205, 95),
        ),
        Scene(
            title="Why it fits the capstone",
            subtitle="Value, architecture, communication, and responsible agent use.",
            bullets=[
                "Track: Agents for Good, focused on biomedical researchers.",
                "Core concepts: Google ADK agents, tool calling, MCP servers, evaluation assets, and structured logging.",
                "Deliverables: public codebase, Kaggle writeup, demo script, screenshots, deployment guide, and narrated video.",
                "Safety: injection checks, input validation, secure logging, and validation disclaimers.",
            ],
            narration="Finally, this fits the Kaggle capstone rubric. The problem is meaningful. The solution uses Google ADK agents, MCP style tools, structured logging, evaluation assets, Docker, and documentation. The demo communicates the architecture clearly, then shows the codebase, then proves the end to end workflow. PharmaGenie is an AI driven drug discovery assistant focused on responsible, evidence grounded research acceleration.",
            accent=(90, 205, 255),
        ),
    ]

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    clips: list[Path] = []
    for i, scene in enumerate(scenes, start=1):
        image_path = render_scene(scene, i)
        audio_path = OUT_DIR / "audio" / f"scene_{i:02d}.wav"
        clip_path = OUT_DIR / "clips" / f"scene_{i:02d}.mp4"
        generate_tts(scene.narration, audio_path)
        create_scene_video(ffmpeg, image_path, audio_path, clip_path)
        clips.append(clip_path)

    final_video = OUT_DIR / "pharmagenie_kaggle_demo.mp4"
    concatenate(ffmpeg, clips, final_video)
    print(final_video)


if __name__ == "__main__":
    main()

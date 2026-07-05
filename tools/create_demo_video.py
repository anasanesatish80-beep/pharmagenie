"""Create the PharmaGenie Kaggle demo video with narrated audio."""

from __future__ import annotations

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


FONT_TITLE = load_font(66, bold=True)
FONT_SUBTITLE = load_font(31)
FONT_SECTION = load_font(25, bold=True)
FONT_BODY = load_font(24)
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
    draw.text((76, 130), "AI Multi-Agent Drug Discovery Research System", fill=(155, 238, 255), font=FONT_SUBTITLE)
    draw.line((76, 182, 655, 182), fill=scene.accent, width=4)


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
            y += 34
        y += 18
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
        ("FastAPI backend", x + 360, y),
        ("Coordinator agent", x + 720, y),
        ("Planner agent", x + 720, y + 145),
        ("ADK specialist agents", x + 360, y + 290),
        ("MCP tool layer", x + 720, y + 290),
        ("PubMed UniProt PubChem Trials", x, y + 435),
        ("Gemini synthesis and report", x + 720, y + 435),
    ]
    for label, bx, by in boxes:
        box = (bx, by, bx + 300, by + 112)
        rounded_rect(draw, box, fill=(10, 34, 52), outline=accent)
        lines = wrap(draw, label, FONT_SECTION, 242)
        text_y = by + max(20, (112 - len(lines) * 31) // 2)
        for line in lines[:3]:
            draw.text((bx + 24, text_y), line, fill=(238, 252, 255), font=FONT_SECTION)
            text_y += 31

    for start, end in [
        ((x + 300, y + 56), (x + 360, y + 56)),
        ((x + 660, y + 56), (x + 720, y + 56)),
        ((x + 870, y + 112), (x + 870, y + 145)),
        ((x + 720, y + 201), (x + 660, y + 346)),
        ((x + 660, y + 346), (x + 720, y + 346)),
        ((x + 870, y + 402), (x + 870, y + 435)),
        ((x + 300, y + 491), (x + 720, y + 346)),
    ]:
        draw.line((start, end), fill=(120, 245, 220), width=4)
        draw.ellipse((end[0] - 6, end[1] - 6, end[0] + 6, end[1] + 6), fill=(120, 245, 220))


def draw_codebase(draw: ImageDraw.ImageDraw) -> None:
    rounded_rect(draw, (104, 418, 1816, 914), fill=(8, 24, 38), outline=(93, 196, 230))
    columns = [
        (
            150,
            468,
            "Agent layer",
            [
                "app/agent.py",
                "CoordinatorAgent",
                "PlannerAgent",
                "LiteratureAgent",
                "ProteinAgent",
                "CompoundAgent",
                "ClinicalTrialAgent",
                "EvidenceRankingAgent",
                "ReportAgent",
            ],
        ),
        (
            630,
            468,
            "Tool and data layer",
            [
                "mcp_servers/adk_tools.py",
                "pubmed_server.py",
                "uniprot_server.py",
                "pubchem_server.py",
                "clinical_trials_server.py",
                "sources/pubmed.py",
                "sources/uniprot.py",
                "sources/pubchem.py",
            ],
        ),
        (
            1110,
            468,
            "Product layer",
            [
                "api/main.py",
                "ui/streamlit_app.py",
                "ai/synthesis.py",
                "safety.py",
                "reports/",
                "tests/",
                "Dockerfile",
                ".github/workflows/",
            ],
        ),
    ]
    for x, y, heading, rows in columns:
        draw.text((x, y), heading, fill=(120, 245, 220), font=FONT_SECTION)
        y += 54
        for row in rows:
            draw.text((x, y), row, fill=(225, 240, 245), font=FONT_BODY)
            y += 42


def render_scene(scene: Scene, index: int) -> Path:
    image = Image.new("RGB", (WIDTH, HEIGHT), (7, 14, 25))
    draw = ImageDraw.Draw(image)
    draw_background(draw, scene.accent)
    draw_header(draw, scene)

    draw.text((76, 228), scene.title, fill=(255, 255, 255), font=FONT_TITLE)
    subtitle_width = 1500 if scene.screenshot else 1020
    for i, line in enumerate(wrap(draw, scene.subtitle, FONT_SUBTITLE, subtitle_width)):
        draw.text((80, 308 + i * 40), line, fill=(178, 211, 222), font=FONT_SUBTITLE)

    if scene.screenshot:
        paste_screenshot(image, scene.screenshot, (240, 380, 1680, 980))
    elif "architecture" in scene.title.lower():
        draw_bullets(draw, 88, 424, scene.bullets, 560)
        draw_architecture(draw, 680, 390, scene.accent)
    elif "codebase" in scene.title.lower():
        draw_codebase(draw)
    else:
        rounded_rect(draw, (82, 430, 1838, 920), fill=(9, 28, 44), outline=(45, 128, 155))
        draw_bullets(draw, 126, 486, scene.bullets, 1600)

    if not scene.screenshot:
        draw.text(
            (76, 1006),
            "PharmaGenie | Google ADK multi-agent workflow | MCP tools | Gemini synthesis",
            fill=(140, 180, 194),
            font=FONT_SMALL,
        )
    path = OUT_DIR / "frames" / f"scene_{index:02d}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    return path


def generate_tts(text: str, output: Path) -> None:
    escaped = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )
    ssml = f"""<speak version='1.0' xml:lang='en-US'>
<voice gender='female'>
<prosody rate='-7%' pitch='+2st'>{escaped}</prosody>
</voice>
</speak>"""
    script = f"""
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SelectVoice('Microsoft Zira Desktop')
$synth.Rate = -1
$synth.Volume = 100
$synth.SetOutputToWaveFile('{output}')
$synth.SpeakSsml(@'
{ssml}
'@)
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
            title="What I built",
            subtitle="A biomedical research system that turns a disease question into ranked in-silico discovery hypotheses.",
            bullets=[
                "The user enters a disease area and a research goal.",
                "Specialized agents gather literature, protein, compound, and clinical trial evidence.",
                "The system ranks early target and candidate ideas for lab follow-up.",
                "Every result is presented as a research hypothesis, not as medical advice.",
            ],
            narration="Hi, this is PharmaGenie. I built it as an AI driven drug discovery research system. The idea is simple: a researcher gives it a disease area and a goal, and the application gathers biomedical evidence, reasons across that evidence with multiple agents, and returns ranked in silico hypotheses that could be explored further in the lab. It is not a treatment tool, and it does not claim a drug is validated. It is meant to speed up early research triage.",
        ),
        Scene(
            title="System architecture",
            subtitle="The application is split into a user interface, an API, an agent workflow, and trusted biomedical data tools.",
            bullets=[
                "Streamlit provides the research console and live workflow view.",
                "FastAPI exposes the backend workflow through clean REST endpoints.",
                "Google ADK coordinates the agent graph.",
                "MCP-style tools connect the agents to scientific sources and report generation.",
            ],
            narration="Here is the architecture. The Streamlit interface is the research console. It talks to a FastAPI backend, and the backend starts the agent workflow. A coordinator agent accepts the task. A planner agent breaks it into smaller research jobs. Then the specialist agents work on literature, proteins, compounds, clinical trials, evidence ranking, and the final report. The tool layer is separated behind MCP style boundaries, so source access is explicit and testable.",
            accent=(120, 245, 210),
        ),
        Scene(
            title="Codebase walkthrough",
            subtitle="The project is organized so each agent, tool, source client, and product surface can be tested separately.",
            bullets=[],
            narration="The codebase follows the same structure as the architecture. The app folder contains the Google ADK root agent. The agents package contains the individual research roles. The MCP server package exposes the tool functions. The sources package contains the PubMed, UniProt, PubChem, and Clinical Trials clients. The product layer contains FastAPI, Streamlit, Gemini synthesis, report generation, safety checks, tests, Docker, and GitHub Actions. I kept these pieces separate so the system is easier to debug and extend.",
            accent=(120, 245, 210),
        ),
        Scene(
            title="End-to-end demo input",
            subtitle="The first screen asks for the disease and the research objective, then starts the agent run.",
            bullets=[],
            narration="Now I will walk through the user experience. On the first screen, the researcher enters the disease and the research objective. The examples are there to make the demo repeatable, but the same fields accept custom questions. The UI is intentionally more like a scientific command console than a generic form, because the product is meant for research work.",
            screenshot="01-streamlit-input-console.png",
            accent=(90, 205, 255),
        ),
        Scene(
            title="Start the workflow",
            subtitle="The Run Discovery Workflow button launches the agent system from the Streamlit console.",
            bullets=[],
            narration="After the disease and objective are set, the researcher presses Run Discovery Workflow. That button starts the backend workflow, sends the request through the API, and begins the agent sequence. In this demo the disease is glioblastoma, and the goal is to generate and prioritize in silico target and candidate hypotheses from biomedical evidence.",
            screenshot="03-discovery-hypotheses.png",
            accent=(90, 205, 255),
        ),
        Scene(
            title="Agents executing live",
            subtitle="The application shows the workflow stages while the agents run.",
            bullets=[],
            narration="When the run starts, the application shows the agents as active stages. This is useful during a demo, but it is also useful for real users because they can understand what the system is doing. The workflow starts with validation and planning, then moves through evidence collection, compound and target reasoning, clinical trial context, ranking, and report generation.",
            screenshot="02-agent-swarm-running.png",
            accent=(180, 135, 255),
        ),
        Scene(
            title="Ranked Discovery Hypotheses",
            subtitle="The first output tab ranks target ideas and shows mechanism, confidence, rationale, and risk notes.",
            bullets=[],
            narration="When the workflow finishes, the first output is Ranked Discovery Hypotheses. Here PharmaGenie shows target hypotheses such as PTEN and NIPSNAP2, with scores, mechanism text, a candidate strategy, rationale, supporting source tags, and a risk note. This is the core discovery output: it gives a researcher a prioritized list of ideas to review.",
            screenshot="05-ranked-discovery-hypotheses.png",
            accent=(100, 245, 210),
        ),
        Scene(
            title="Evidence Matrix",
            subtitle="The second output tab keeps the evidence transparent across PubMed, UniProt, PubChem, and ClinicalTrials.gov.",
            bullets=[],
            narration="The Evidence Matrix tab shows where the system pulled evidence from and how confident each source signal is. This makes the output easier to inspect. Instead of only returning a polished summary, the app shows source, title, confidence, retrieval mode, URL, and summary context so a researcher can audit the dossier.",
            screenshot="06-evidence-matrix.png",
            accent=(100, 245, 210),
        ),
        Scene(
            title="Research Dossier",
            subtitle="The Dossier tab turns the agent output into a readable report with disease, goal, and Executive Summary.",
            bullets=[],
            narration="The Dossier tab turns the workflow into a readable research report. It clearly states PharmaGenie Research Dossier: glioblastoma, includes the research goal, and opens with an Executive Summary. That summary explains that the system generated an in silico drug discovery dossier, prioritized evidence backed hypotheses, and still requires human review and experimental follow up.",
            screenshot="07-research-dossier-summary.png",
            accent=(100, 245, 210),
        ),
        Scene(
            title="Backend and deployability",
            subtitle="The backend is exposed through FastAPI and can be run locally or packaged for cloud deployment.",
            bullets=[],
            narration="The backend is built as a FastAPI service. The interactive docs expose the health, research, and discovery endpoints. API keys and configuration come from environment variables, not hard coded files. Docker and docker compose make the app repeatable locally, and the same pattern can be moved to Cloud Run for a hosted version.",
            screenshot="04-fastapi-docs.png",
            accent=(255, 205, 95),
        ),
        Scene(
            title="Responsible discovery workflow",
            subtitle="The goal is faster biomedical research triage, with safety controls around how the system accepts and presents information.",
            bullets=[
                "Prompt injection and unsafe medical advice requests are screened.",
                "Source text is treated as evidence, not as instructions.",
                "Logs avoid secrets and sensitive values.",
                "Reports clearly mark outputs as hypotheses requiring validation.",
            ],
            narration="The last piece is safety. Biomedical tools need careful boundaries. PharmaGenie screens prompt injection, blocks patient specific medical advice, treats source text as evidence rather than instructions, and avoids logging secrets. The final report is useful because it gives researchers a structured starting point, while still making it clear that laboratory validation is required.",
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

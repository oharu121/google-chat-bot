import logging

from cards import build_progressive_card
from chat_api import ChatApiClient
from models import PipelineState, PipelineStatus, Step, StepStatus
from throttle import ThrottledPatcher

logger = logging.getLogger(__name__)


def process_message(space_name, user_text, sender, user_message_name=None, chat_client=None):
    if chat_client is None:
        chat_client = ChatApiClient()

    state = PipelineState(
        steps=[
            Step(id="analyze", label="問い合わせを解析中"),
            Step(id="build_query", label="検索クエリを作成中"),
            Step(id="fetch_kb", label="ナレッジベースを検索中"),
            Step(id="generate", label="回答を生成中"),
        ],
        sender=sender,
    )

    try:
        initial_body = build_progressive_card(state)
        message_name = chat_client.create_message(space_name, initial_body)
    except Exception:
        logger.error("Failed to create initial card", exc_info=True)
        return

    patcher = ThrottledPatcher(chat_client, message_name)

    try:
        # Step 1: Analyze
        _advance_step(state, "analyze", patcher, message_name)
        _complete_step(state, "analyze", patcher, message_name)

        # Step 2: Build search query
        _advance_step(state, "build_query", patcher, message_name)
        state.steps[1].detail = f"「{user_text}」"
        _complete_step(state, "build_query", patcher, message_name)

        # Step 3: Fetch KB
        _advance_step(state, "fetch_kb", patcher, message_name)
        _complete_step(state, "fetch_kb", patcher, message_name)

        # Step 4: Generate answer (multiple paragraphs for streaming effect)
        _advance_step(state, "generate", patcher, message_name)

        paragraphs = [
            f"{sender}さん、お問い合わせありがとうございます。「{user_text}」について回答いたします。",
            "現在、ナレッジベースの情報を基に回答を生成しています。こちらはデモ用のテキストですが、実際の運用ではRAGパイプラインから取得した情報が表示されます。",
            "回答の品質向上のため、複数のソースを参照し、関連性の高い情報を統合しています。ナレッジベースには社内ドキュメント、FAQ、過去の問い合わせ履歴などが含まれています。",
            "以上が現時点での回答となります。追加のご質問がございましたら、お気軽にお問い合わせください。フィードバックボタンで回答の品質をお知らせいただけると幸いです。",
        ]
        for para in paragraphs:
            state.content_paragraphs.append(para)
            body = build_progressive_card(state, message_name=message_name)
            patcher.patch(body)

        _complete_step(state, "generate", patcher, message_name)

        # Final state
        state.status = PipelineStatus.COMPLETED
        state.current_step_description = "4 ステップ完了"
        final_body = build_progressive_card(state, message_name=message_name)
        patcher.patch(final_body, force=True)
    except Exception:
        logger.error("Failed during pipeline execution", exc_info=True)

    try:
        patcher.flush()
    except Exception:
        logger.error("Failed to flush final patch", exc_info=True)


def _advance_step(state, step_id, patcher, message_name):
    step = next(s for s in state.steps if s.id == step_id)
    step.status = StepStatus.IN_PROGRESS
    state.current_step_description = step.label
    body = build_progressive_card(state, message_name=message_name)
    patcher.patch(body)


def _complete_step(state, step_id, patcher, message_name):
    step = next(s for s in state.steps if s.id == step_id)
    step.status = StepStatus.COMPLETED
    body = build_progressive_card(state, message_name=message_name)
    patcher.patch(body)

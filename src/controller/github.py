from fastapi import FastAPI, Request, Header, HTTPException
import httpx
import random
import os

app = FastAPI()

# GITHUB 에서 MR이 생길때 코드 리뷰를 할 수 있도록 하는 API - MR 의 내용을 분석해서 COMMENT 를 남기도록 하는게 목표

# 깃허브 인증을 위한 토큰 설정 (환경 변수에 저장하는 것이 좋음)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# 임의의 티켓 넘버 생성 함수
def generate_ticket_number():
    return f"TICKET-{random.randint(1000, 9999)}"

@app.post("/webhook")
async def github_webhook(request: Request, x_github_event: str = Header(None)):
    payload = await request.json()

    # PR이 생성되었을 때만 처리
    if x_github_event == "pull_request" and payload.get("action") in ["opened", "reopened"]:
        pr = payload.get("pull_request", {})
        pr_url = pr.get("url")
        comments_url = pr.get("comments_url")
        pr_number = pr.get("number")
        repo_full_name = payload.get("repository", {}).get("full_name")

        if not all([comments_url, pr_number]):
            raise HTTPException(status_code=400, detail="Invalid PR payload")

        ticket_number = generate_ticket_number()
        comment_body = {"body": f"🔖 Auto-generated ticket number: **{ticket_number}**"}

        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        }

        # PR에 코멘트 작성
        async with httpx.AsyncClient() as client:
            response = await client.post(comments_url, headers=headers, json=comment_body)
            if response.status_code != 201:
                raise HTTPException(status_code=500, detail="Failed to post comment")

        return {"message": f"Comment added to PR #{pr_number}", "ticket": ticket_number}

    return {"message": "Ignored event"}

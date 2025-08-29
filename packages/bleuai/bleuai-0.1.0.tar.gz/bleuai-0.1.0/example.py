#!/usr/bin/env python3
import asyncio
import os
from bleuai import BleuAI

async def main():
    client = BleuAI(api_key=os.getenv("BLEU_API_KEY"))
    
    print(f"Running workflow...")
    result = await client.run_workflow(
        workflow_id="9238bbe8-d66f-4597-8d49-f35d02c29b0d",
        inputs={"Image Prompt": "A cake with caption 'Bleu AI'."}
    )
    
    print(result.outputs)
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())

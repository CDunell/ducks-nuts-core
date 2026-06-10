import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

import asyncio
from realtime.run_connector import main

asyncio.run(main())

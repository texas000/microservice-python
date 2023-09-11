import os
import importlib.util

controller_folder = "src/controller"

def include_routers(prefix_router):
    for root, dirs, files in os.walk(controller_folder):
        for file in files:
            file_path = os.path.join(root, file)
            # .py 확장자를 가진 파일만 처리
            if file.endswith(".py"):
                # 모듈 이름 생성
                module_name = os.path.splitext(file)[0]
                
                # 모듈 로드
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # "router" 객체 호출
                if hasattr(module, "router"):
                    prefix_router.include_router(module.router)
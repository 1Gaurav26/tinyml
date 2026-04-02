FROM python:3.11-slim

WORKDIR /training

# Install tensorflow-cpu first so roboflow can't downgrade/conflict it
RUN pip install --no-cache-dir tensorflow-cpu==2.15.0
RUN pip install --no-cache-dir roboflow Pillow numpy

COPY train_model.py .

VOLUME ["/training/data", "/training/out"]

ENTRYPOINT ["python", "train_model.py"]

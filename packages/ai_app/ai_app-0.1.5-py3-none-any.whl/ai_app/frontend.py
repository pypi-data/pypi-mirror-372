import inspect
from typing import Iterable

import gradio as gr

from ai_app.external.providers import filter_common_model_names, get_common_models_meta_attributes


def build_model_choice_dropdown(
    models: Iterable[str] | None = None, max_cost: float = 5.0
) -> gr.Dropdown:
    common_models = get_common_models_meta_attributes()
    models = models or filter_common_model_names(max_cost=max_cost, supports_system_messages=True)
    choices = []
    for model in models:
        if attr := common_models.get(model):
            model = (f"{model} ({attr.get_relative_cost_representation()})", model)

        choices.append(model)

    model_choice = gr.Dropdown(choices, label="Model")
    return model_choice


def get_voice_activity_javascript():
    """
    Taken from https://www.gradio.app/guides/automatic-voice-detection#voice-activity-detection-for-hands-free-interaction
    This version detects only end of speech, and clicks the stop recording button,
    while the full version can detect start of speech also.
    """
    js = """
        async function main() {
            const script1 = document.createElement("script");
            script1.src = "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.14.0/dist/ort.js";
            document.head.appendChild(script1);
            const script2 = document.createElement("script");
            script2.onload = async () =>  {
                console.log("vad loaded") ;
                var record = document.querySelector('.record-button');
                record.textContent = "Record"
                record.style = "width: fit-content; padding-right: 0.5vw;"
                const myvad = await vad.MicVAD.new(
                    {
                        onSpeechEnd: (audio) => {
                            var stop = document.querySelector('.stop-button');
                            if (stop != null) {
                                console.log(stop);
                                stop.click();
                            }
                        }
                    }
                );
                myvad.start();
            };
            script2.src = "https://cdn.jsdelivr.net/npm/@ricky0123/vad-web@0.0.7/dist/bundle.min.js";
            script1.onload = () =>  {
                console.log("onnx loaded") 
                document.head.appendChild(script2)
            };
        }
    """
    return js


def get_generating_text_javascript() -> str:
    js = inspect.cleandoc("""
    () => {
        // Function to start the animation on a specific element
        function startGeneratingAnimation(element) {
            // Ensure we don't attach multiple animations to the same element
            if (element.dataset.animated) return;
            element.dataset.animated = true;

            const animationFrames = ['Generating.', 'Generating..', 'Generating...'];
            let currentFrame = 0;
            
            const intervalId = setInterval(() => {
                // The most reliable way to stop is to check if the element has been
                // removed from the page. Gradio will replace it with the final response.
                if (!document.body.contains(element)) {
                    clearInterval(intervalId);
                    return;
                }

                element.textContent = animationFrames[currentFrame];
                currentFrame = (currentFrame + 1) % animationFrames.length;
            }, 400);
        }

        // Use a MutationObserver to watch for when our specific element is added to the DOM
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    // We only care about element nodes
                    if (node.nodeType !== 1) return;

                    // Check if the new node is our target element
                    if (node.id === 'gradio-generating-spinner') {
                        startGeneratingAnimation(node);
                    } 
                    // Also check if our target is a child of the new node
                    else {
                        const targetElement = node.querySelector('#gradio-generating-spinner');
                        if (targetElement) {
                            startGeneratingAnimation(targetElement);
                        }
                    }
                });
            });
        });

        // Start observing the entire document body for added nodes
        observer.observe(document.body, { childList: true, subtree: true });
    }
    """)
    return js


def get_generating_text_span() -> str:
    span = '<span id="gradio-generating-spinner" style="color: #888;">Generating...</span>'
    return span

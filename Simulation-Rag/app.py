from fasthtml.common import *
from retriever import llm_call

app, rt = fast_app(live=True)

# Store chat history
chat_history = []

@rt("/")
def get():
    chat_display = Div(
        *[Div(
            Div(Strong("Question: "), msg["query"], cls="user-message"),
            Div(Strong("Summary: "), msg["response"], cls="ai-message"),
            Div(Small(f"(Mode: {msg['mode']} | Company Skill: {msg['company_skill']} | Target Industry: {msg['target_industry']} | Start Date: {msg['start_date']} | Retrieved {msg['top_k']} documents)"), style="color: #666; font-style: italic;"),
            cls="message-pair"
        ) for msg in chat_history],
        id="chat-history",
        style="max-height: 400px; overflow-y: auto; margin-bottom: 20px; padding: 10px; border: 1px solid #ccc; border-radius: 5px;"
    )
    
    return Titled("AI Simulation RAG System",
        chat_display,
        Form(
            # Top row: Controls on left, Question box on right
            Div(
                # Left side - Controls
                Div(
                    Div(
                        Label("Number of documents to retrieve: ", 
                              Input(type="range", name="top_k", min="1", max="20", value="5", 
                                    id="top_k_slider",
                                    style="width: 200px; margin-left: 10px; margin-right: 10px;"),
                              Span("5", id="top_k_value", style="font-weight: bold;"),
                              style="display: flex; align-items: center; margin-bottom: 15px;"
                        ),
                        Script("""
                            const slider = document.getElementById('top_k_slider');
                            const valueDisplay = document.getElementById('top_k_value');
                            slider.addEventListener('input', function() {
                                valueDisplay.textContent = this.value;
                            });
                        """)
                    ),
                    Div(
                        Label("Mode: ",
                              Select(
                                  Option("Standard", value="standard", selected=True),
                                  Option("Compare", value="compare"),
                                  name="mode",
                                  id="mode_select",
                                  style="padding: 8px; margin-left: 10px; border-radius: 4px; width: 200px;"
                              ),
                              style="display: flex; align-items: center; margin-bottom: 15px;"
                        )
                    ),
                    style="flex: 0 0 auto; padding-right: 30px;"
                ),
                # Right side - Question box
                Div(
                    Input(name="question", placeholder="Ask a question ...", 
                          style="width: 100%; padding: 10px; height: 100px; border: 1px solid #ccc; border-radius: 4px;"),
                    style="flex: 1;"
                ),
                style="display: flex; align-items: flex-start; margin-bottom: 30px;"
            ),
            Div(
                # Standard mode fields
                Div(
                    Div(
                        Label("Company Skills: ",
                              Select(
                                  Option("Real-Time Systems", value="Real-Time Systems"),
                                  Option("Regulatory Compliance", value="Regulatory Compliance"),
                                  Option("AI Governance", value="AI Governance"),
                                  Option("Transaction Monitoring", value="Transaction Monitoring"),
                                  name="company_skill",
                                  style="padding: 8px; margin-left: 10px; border-radius: 4px; width: 200px;"
                              ),
                              style="display: flex; align-items: center; margin-bottom: 15px;"
                        )
                    ),
                    Div(
                        Label("Target Industries: ",
                              Select(
                                  Option("Retail Banking", value="Retail Banking"),
                                  Option("Fintech", value="Fintech"),
                                  Option("Healthcare", value="Healthcare"),
                                  name="target_industry",
                                  style="padding: 8px; margin-left: 10px; border-radius: 4px; width: 200px;"
                              ),
                              style="display: flex; align-items: center; margin-bottom: 15px;"
                        )
                    ),
                    Div(
                        Label("Start Date: ",
                              Select(
                                  Option("2020", value="2020"),
                                  Option("2021", value="2021"),
                                  Option("2022", value="2022"),
                                  Option("2023", value="2023"),
                                  Option("2024", value="2024"),
                                  Option("2020-2022", value="2020-2022"),
                                  Option("2021-2023", value="2021-2023"),
                                  Option("2022-2024", value="2022-2024"),
                                  Option("2020-2024", value="2020-2024"),
                                  name="start_date",
                                  style="padding: 8px; margin-left: 10px; border-radius: 4px; width: 200px;"
                              ),
                              style="display: flex; align-items: center; margin-bottom: 15px;"
                        )
                    ),
                    id="standard_fields",
                    style="display: block;"
                ),
                # Compare mode fields
                Div(
                    Div(
                        # Group A
                        Div(
                            H4("Group A", style="margin-bottom: 15px; color: #2c3e50;"),
                            Div(
                                Label("Company Skills: ",
                                      Select(
                                          Option("Real-Time Systems", value="Real-Time Systems"),
                                          Option("Regulatory Compliance", value="Regulatory Compliance"),
                                          Option("AI Governance", value="AI Governance"),
                                          Option("Transaction Monitoring", value="Transaction Monitoring"),
                                          name="company_skill_a",
                                          style="padding: 8px; margin-left: 10px; border-radius: 4px; width: 200px;"
                                      ),
                                      style="display: flex; align-items: center; margin-bottom: 15px;"
                                )
                            ),
                            Div(
                                Label("Target Industries: ",
                                      Select(
                                          Option("Retail Banking", value="Retail Banking"),
                                          Option("Fintech", value="Fintech"),
                                          Option("Healthcare", value="Healthcare"),
                                          name="target_industry_a",
                                          style="padding: 8px; margin-left: 10px; border-radius: 4px; width: 200px;"
                                      ),
                                      style="display: flex; align-items: center; margin-bottom: 15px;"
                                )
                            ),
                            Div(
                                Label("Start Date: ",
                                      Select(
                                          Option("2020", value="2020"),
                                          Option("2021", value="2021"),
                                          Option("2022", value="2022"),
                                          Option("2023", value="2023"),
                                          Option("2024", value="2024"),
                                          Option("2020-2022", value="2020-2022"),
                                          Option("2021-2023", value="2021-2023"),
                                          Option("2022-2024", value="2022-2024"),
                                          Option("2020-2024", value="2020-2024"),
                                          name="start_date_a",
                                          style="padding: 8px; margin-left: 10px; border-radius: 4px; width: 200px;"
                                      ),
                                      style="display: flex; align-items: center; margin-bottom: 15px;"
                                )
                            ),
                            style="flex: 1; padding-right: 20px;"
                        ),
                        # Group B
                        Div(
                            H4("Group B", style="margin-bottom: 15px; color: #2c3e50;"),
                            Div(
                                Label("Company Skills: ",
                                      Select(
                                          Option("Real-Time Systems", value="Real-Time Systems"),
                                          Option("Regulatory Compliance", value="Regulatory Compliance"),
                                          Option("AI Governance", value="AI Governance"),
                                          Option("Transaction Monitoring", value="Transaction Monitoring"),
                                          name="company_skill_b",
                                          style="padding: 8px; margin-left: 10px; border-radius: 4px; width: 200px;"
                                      ),
                                      style="display: flex; align-items: center; margin-bottom: 15px;"
                                )
                            ),
                            Div(
                                Label("Target Industries: ",
                                      Select(
                                          Option("Retail Banking", value="Retail Banking"),
                                          Option("Fintech", value="Fintech"),
                                          Option("Healthcare", value="Healthcare"),
                                          name="target_industry_b",
                                          style="padding: 8px; margin-left: 10px; border-radius: 4px; width: 200px;"
                                      ),
                                      style="display: flex; align-items: center; margin-bottom: 15px;"
                                )
                            ),
                            Div(
                                Label("Start Date: ",
                                      Select(
                                          Option("2020", value="2020"),
                                          Option("2021", value="2021"),
                                          Option("2022", value="2022"),
                                          Option("2023", value="2023"),
                                          Option("2024", value="2024"),
                                          Option("2020-2022", value="2020-2022"),
                                          Option("2021-2023", value="2021-2023"),
                                          Option("2022-2024", value="2022-2024"),
                                          Option("2020-2024", value="2020-2024"),
                                          name="start_date_b",
                                          style="padding: 8px; margin-left: 10px; border-radius: 4px; width: 200px;"
                                      ),
                                      style="display: flex; align-items: center; margin-bottom: 15px;"
                                )
                            ),
                            style="flex: 1; padding-left: 20px;"
                        ),
                        style="display: flex; gap: 20px;"
                    ),
                    id="compare_fields",
                    style="display: none;"
                ),
                # Submit button
                Div(
                    Button("Submit", type="submit", style="padding: 10px 20px; background-color: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; width: auto;"),
                    style="margin-top: 20px;"
                ),
                Script("""
                    const modeSelect = document.getElementById('mode_select');
                    const standardFields = document.getElementById('standard_fields');
                    const compareFields = document.getElementById('compare_fields');
                    
                    modeSelect.addEventListener('change', function() {
                        if (this.value === 'compare') {
                            standardFields.style.display = 'none';
                            compareFields.style.display = 'block';
                        } else {
                            standardFields.style.display = 'block';
                            compareFields.style.display = 'none';
                        }
                    });
                """)
            ),
            method="post",
            action="/ask"
        )
    )

@rt("/ask")
def post(question: str, top_k: int = 5, mode: str = "standard", 
         company_skill: str = "", target_industry: str = "", start_date: str = "",
         company_skill_a: str = "", target_industry_a: str = "", start_date_a: str = "",
         company_skill_b: str = "", target_industry_b: str = "", start_date_b: str = ""):
    if question.strip():
        # Get response from RAG system with specified top_k
        response = llm_call(question, use_rag=True, top_k=top_k)
        
        # Prepare data based on mode
        if mode == "compare":
            chat_data = {
                "query": question,
                "response": response,
                "top_k": top_k,
                "mode": mode,
                "company_skill": f"A: {company_skill_a}, B: {company_skill_b}",
                "target_industry": f"A: {target_industry_a}, B: {target_industry_b}",
                "start_date": f"A: {start_date_a}, B: {start_date_b}"
            }
        else:
            chat_data = {
                "query": question,
                "response": response,
                "top_k": top_k,
                "mode": mode,
                "company_skill": company_skill or "Real-Time Systems",
                "target_industry": target_industry or "Retail Banking",
                "start_date": start_date or "2024"
            }
        
        # Add to chat history
        chat_history.append(chat_data)
    
    # Redirect back to home to show updated chat
    return RedirectResponse("/", status_code=303)

serve()


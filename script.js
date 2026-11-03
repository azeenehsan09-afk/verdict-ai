
const decisionForm = document.getElementById("decision-form");
const decisionInput = document.getElementById("decision-input");
const courtroom = document.getElementById("courtroom");

const submitButton = decisionForm.querySelector("button");

// Handle form submission
decisionForm.addEventListener("submit", async function(event) {

    event.preventDefault();

    const decision = decisionInput.value.trim();

    if (decision === "") {
        alert("Please enter your decision first!");
        return;
    }

    courtroom.classList.add("active");

    document.getElementById("submitted-decision").textContent =
        '"' + decision + '"';

    courtroom.scrollIntoView({ behavior: "smooth" });

    const responseIds = [
        "optimist-response",
        "skeptic-response",
        "realist-response"
    ];

    responseIds.forEach(function(id) {
        document.getElementById(id).textContent =
            "Thinking... Your AI perspective is being prepared.";
    });

    document.getElementById("verdict-decision").textContent =
        "Preparing verdict...";

    document.getElementById("judge-reasoning").textContent =
        "The Judge is evaluating both sides.";

    document.getElementById("overlooked-question").textContent =
        "Finding the question you might have missed.";

    document.getElementById("confidence-value").textContent = "0%";
    document.getElementById("confidence-fill").style.width = "0%";

    // Clear previous appeal
    document.getElementById("appeal-result").innerHTML = "";
    document.getElementById("appeal-input").value = "";

    submitButton.disabled = true;
    submitButton.textContent = "Analyzing Decision...";

    try {

        const response = await fetch("http://127.0.0.1:5000/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                decision: decision
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "AI analysis failed.");
        }

        document.getElementById("optimist-response").textContent =
            result.optimist;

        document.getElementById("skeptic-response").textContent =
            result.skeptic;

        document.getElementById("realist-response").textContent =
            result.realist;

        const judge = result.judge;

        // Display original verdict
        const verdictElement =
            document.getElementById("verdict-decision");

        verdictElement.textContent = judge.verdict;

        verdictElement.classList.remove(
            "verdict-proceed",
            "verdict-caution",
            "verdict-reconsider"
        );

        if (judge.verdict === "PROCEED") {
            verdictElement.classList.add("verdict-proceed");
        } else if (judge.verdict === "PROCEED WITH CAUTION") {
            verdictElement.classList.add("verdict-caution");
        } else {
            verdictElement.classList.add("verdict-reconsider");
        }

        // Display conditions that could change the verdict
        const changesList =
            document.getElementById("verdict-changes");

        changesList.innerHTML = "";

        judge.what_would_change.forEach(function(condition) {
            const listItem = document.createElement("li");
            listItem.textContent = condition;
            changesList.appendChild(listItem);
        });

        document.getElementById("judge-reasoning").textContent =
            judge.reasoning;

        document.getElementById("overlooked-question").textContent =
            judge.overlooked_question;

        document.getElementById("confidence-value").textContent =
            judge.confidence + "%";

        document.getElementById("confidence-fill").style.width =
            judge.confidence + "%";

    } catch (error) {

        console.error("Verdict Error:", error);

        responseIds.forEach(function(id) {
            document.getElementById(id).textContent = error.message;
        });

        document.getElementById("verdict-decision").textContent =
            "Verdict unavailable";

        document.getElementById("judge-reasoning").textContent =
            error.message;

    } finally {

        submitButton.disabled = false;
        submitButton.textContent = "Put My Decision on Trial →";

    }

});


// ===================================
// APPEAL ROUND
// ===================================

const appealButton = document.getElementById("appeal-button");

appealButton.addEventListener("click", async function() {

    const appealInput = document.getElementById("appeal-input");
    const appealResult = document.getElementById("appeal-result");

    const appealText = appealInput.value.trim();

    if (appealText.length < 10) {
        alert("Please explain your appeal in a little more detail.");
        return;
    }

    const decision = decisionInput.value.trim();

    const originalVerdict =
        document.getElementById("verdict-decision").textContent.trim();

    const originalReasoning =
        document.getElementById("judge-reasoning").textContent.trim();

    if (
        !decision ||
        originalVerdict === "Preparing verdict..." ||
        originalVerdict === "Verdict unavailable"
    ) {
        alert("Please submit a decision and receive an original verdict first.");
        return;
    }

    appealButton.disabled = true;
    appealButton.textContent = "Judge is Reconsidering...";

    appealResult.textContent =
        "The Judge is reviewing your new information...";

    try {

        const response = await fetch("http://127.0.0.1:5000/appeal", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                decision: decision,
                original_verdict: originalVerdict,
                original_reasoning: originalReasoning,
                appeal: appealText
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Appeal failed.");
        }

        appealResult.innerHTML = "";

        // Create revised Judge panel
        const card = document.createElement("div");
        card.className = "revised-verdict-card";

        // Heading
        const heading = document.createElement("h3");
        heading.textContent = "⚖ The Judge — Reconsideration";

        // Verdict box: same structure as original Judge
        const verdictBox = document.createElement("div");
        verdictBox.className = "verdict-result";

        const verdictLabel = document.createElement("p");
        verdictLabel.className = "verdict-label";
        verdictLabel.textContent = "REVISED VERDICT";

        const verdict = document.createElement("h2");
        verdict.textContent = result.verdict;
        verdict.className = "revised-verdict";

        if (result.verdict === "PROCEED") {
            verdict.classList.add("verdict-proceed");
        } else if (result.verdict === "PROCEED WITH CAUTION") {
            verdict.classList.add("verdict-caution");
        } else {
            verdict.classList.add("verdict-reconsider");
        }

        verdictBox.append(verdictLabel, verdict);

        // Judge's reasoning
        const reasoningBox = document.createElement("div");
        reasoningBox.className = "judge-detail";

        const reasoningHeading = document.createElement("h4");
        reasoningHeading.textContent = "Judge's Reasoning";

        const reasoning = document.createElement("p");
        reasoning.textContent = result.reasoning;

        reasoningBox.append(reasoningHeading, reasoning);

        // Overlooked question
        const questionBox = document.createElement("div");
        questionBox.className = "judge-detail question-box";

        const questionHeading = document.createElement("h4");
        questionHeading.textContent = "The Overlooked Question";

        const question = document.createElement("p");
        question.textContent = result.overlooked_question;

        questionBox.append(questionHeading, question);

        // Status explanation
        const status = document.createElement("p");
        status.className = "appeal-status-text";

        status.textContent = result.verdict_changed
            ? "The Judge has changed the original verdict based on your new information."
            : "After reviewing your appeal, the Judge has maintained the original verdict.";

        // Assemble the revised Judge panel
        card.append(
            heading,
            verdictBox,
            status,
            reasoningBox,
            questionBox
        );

        appealResult.appendChild(card);
// Show the final reflection section after the appeal
const finalReflection = document.getElementById("final-reflection");
const finalQuestion = document.getElementById("final-question");

finalQuestion.textContent = result.overlooked_question;

finalReflection.hidden = false;

finalReflection.scrollIntoView({
    behavior: "smooth",
    block: "start"
});
        appealResult.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });

    } catch (error) {

        console.error("Appeal Error:", error);
        appealResult.textContent = error.message;

    } finally {

        appealButton.disabled = false;
        appealButton.textContent = "Challenge the Verdict →";

    }

});

// ===================================
// FINAL VERDICT ROUND
// ===================================

const finalForm = document.getElementById("final-form");

finalForm.addEventListener("submit", async function(event) {

    // Prevent the page from refreshing
    event.preventDefault();

    const finalAnswer = document.getElementById("final-answer").value.trim();
    const finalSubmit = document.getElementById("final-submit");

    if (finalAnswer.length < 5) {
        alert("Please provide a little more detail in your answer.");
        return;
    }

    // Get the revised verdict and reasoning from the appeal panel
    const revisedVerdictElement =
        document.querySelector("#appeal-result .revised-verdict");

    const revisedReasoningElement =
        document.querySelector("#appeal-result .judge-detail:not(.question-box) p");

    const overlookedQuestionElement =
        document.querySelector("#appeal-result .question-box p");

    if (!revisedVerdictElement || !revisedReasoningElement || !overlookedQuestionElement) {
        alert("Please complete the appeal round first.");
        return;
    }

    const decision = decisionInput.value.trim();

    const revisedVerdict = revisedVerdictElement.textContent.trim();
    const revisedReasoning = revisedReasoningElement.textContent.trim();
    const overlookedQuestion = overlookedQuestionElement.textContent.trim();

    finalSubmit.disabled = true;
    finalSubmit.textContent = "The Judge is Reaching a Final Decision...";

    try {

        const response = await fetch("http://127.0.0.1:5000/finalize", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                decision: decision,
                revised_verdict: revisedVerdict,
                revised_reasoning: revisedReasoning,
                overlooked_question: overlookedQuestion,
                user_answer: finalAnswer
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Final verdict failed.");
        }

        // Display the final verdict
        document.getElementById("final-verdict-decision").textContent =
            result.final_verdict;

        document.getElementById("final-reasoning").textContent =
            result.final_reasoning;

        document.getElementById("final-next-step").textContent =
            result.next_step;

        document.getElementById("final-closing-message").textContent =
            result.closing_message;

        // Show final result and hide the reflection form
        document.getElementById("final-reflection").hidden = true;

        const finalResult = document.getElementById("final-result");
        finalResult.hidden = false;

        finalResult.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    } catch (error) {

        console.error("Final Verdict Error:", error);
        alert(error.message);

    } finally {

        finalSubmit.disabled = false;
        finalSubmit.textContent = "Deliver Final Verdict →";

    }

});

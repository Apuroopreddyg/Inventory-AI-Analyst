import { useState } from "react";
import { sendChatMessage, submitApproval } from "./services/api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./App.css";

function App() {
	const [messages, setMessages] = useState([]);
	const [input, setInput] = useState("");
	const [threadId, setThreadId] = useState(null);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");
	const [mode, setMode] = useState("multi-agent");

	async function handleSendMessage(e) {
		e.preventDefault();

		if (!input.trim() || loading) return;

		const question = input.trim();

		setMessages((prev) => [...prev, { role: "user", content: question }]);

		setInput("");
		setLoading(true);
		setError("");

		try {
			const data = await sendChatMessage(question, threadId, mode);

			// Save the generated thread ID for this conversation
			setThreadId(data.thread_id);

			if (data.approval_required) {
				setMessages((prev) => [
				...prev,
				{
					role: "approval",
					content: data.approval_details,
					threadId: data.thread_id,
				},
				]);
			} else {
				setMessages((prev) => [
				...prev,
				{
					role: "assistant",
					content: data.response,
				},
				]);
			}
		} catch (err) {
			setError(err.message);
		} finally {
			setLoading(false);
		}
	}

	async function handleApproval(messageIndex, decision, approvalMessage) {
		setLoading(true);
		setError("");

		try {
		const data = await submitApproval(approvalMessage.threadId, decision);

		// Replace the approval card with its completed status
		setMessages((prev) => {
			const updated = [...prev];

			updated[messageIndex] = {
			role: "approval_result",
			content:
			decision === "approve"
				? "Action approved and executed successfully."
				: "Action rejected. No inventory changes were made.",
			};

			updated.push({
			role: "assistant",
			content: data.response,
			});

			return updated;
		});
		} catch (err) {
		setError(err.message);
		} finally {
		setLoading(false);
		}
	}

	return (
		<div className="app-container">
		<aside className="sidebar">
			<div className="brand">
			<div className="brand-icon">📦</div>
			<h2>Inventory AI</h2>
			</div>

			<button
			className="new-chat-button"
			onClick={() => {
				setMessages([]);
				setThreadId(null);
				setError("");
			}}
			>
			+ New Conversation
			</button>

			<div className="sidebar-info">
			<p>AI Inventory Assistant</p>
			<span>Powered by LangGraph</span>
			</div>
		</aside>

		<main className="chat-container">
			<header className="chat-header">
				<div>
					<h2>Inventory AI Analyst</h2>
					<p>Ask questions about your inventory</p>
				</div>

				<div className="status-indicator">
					<span className="status-dot"></span>
					AI Assistant
				</div>
				<select
					value={mode}
					onChange={(e) => {
						setMode(e.target.value);
						setMessages([]);
						setThreadId(null);
					}}
					className="mode-selector"
					>
					<option value="multi-agent">Multi-Agent</option>
					<option value="hitl">HITL Agent</option>
				</select>
			</header>

			<section className="messages-container">
			{messages.length === 0 && (
				<div className="welcome-screen">
				<div className="welcome-icon">📊</div>
				<h1>How can I help you today?</h1>
				<p>
					Analyze stock levels, check deliveries, and manage inventory
					using natural language.
				</p>

				<div className="suggestion-cards">
					<button
					onClick={() =>
						setInput("Which products are running low on stock?")
					}
					>
					<span>📉</span>
					<strong>Low stock analysis</strong>
					<small>Identify products below reorder levels</small>
					</button>

					<button
					onClick={() =>
						setInput("Which vendors have pending deliveries?")
					}
					>
					<span>🚚</span>
					<strong>Pending deliveries</strong>
					<small>Check outstanding vendor deliveries</small>
					</button>

					<button
					onClick={() => setInput("Show inventory received this month")}
					>
					<span>📦</span>
					<strong>Monthly inventory</strong>
					<small>Review this month's received stock</small>
					</button>

					<button
					onClick={() => setInput("Please reorder 100 units of Router")}
					>
					<span>🔄</span>
					<strong>Reorder inventory</strong>
					<small>Request a reorder with approval</small>
					</button>
				</div>
				</div>
			)}

			{messages.map((message, index) => (
				<div className={`message ${message.role}`} key={index}>
				{message.role === "user" && (
					<div className="message-avatar user-avatar">You</div>
				)}

				{(message.role === "assistant" ||
					message.role === "approval_result") && (
					<div className="message-avatar assistant-avatar">AI</div>
				)}

				<div className="message-content">
					{message.role === "approval" ? (
					<div className="approval-card">
						<div className="approval-header">
						<span>⚠️ Approval Required</span>
						</div>

						<p>
						The AI agent is requesting approval for the following
						action:
						</p>

						<div className="approval-details">
						{message.content.tool === "reorder_inventory" && (
							<>
							<div className="approval-detail">
								<span>Action</span>
								<strong>Reorder Inventory</strong>
							</div>

							<div className="approval-detail">
								<span>Product</span>
								<strong>{message.content.arguments.product}</strong>
							</div>

							<div className="approval-detail">
								<span>Quantity</span>
								<strong>
								{message.content.arguments.quantity} units
								</strong>
							</div>
							</>
						)}

						{message.content.tool === "receive_delivery" && (
							<>
							<div className="approval-detail">
								<span>Action</span>
								<strong>Receive Delivery</strong>
							</div>

							<div className="approval-detail">
								<span>Purchase Order</span>
								<strong>
								{message.content.arguments.po_number}
								</strong>
							</div>
							</>
						)}
						</div>

						<div className="approval-actions">
						<button
							disabled={loading}
							onClick={() =>
							handleApproval(index, "approve", message)
							}
						>
							Approve
						</button>

						<button
							disabled={loading}
							onClick={() => handleApproval(index, "reject", message)}
						>
							Reject
						</button>
						</div>
					</div>
					) : (
					<div className="message-text">
						<ReactMarkdown remarkPlugins={[remarkGfm]}>
							{message.content}
						</ReactMarkdown>
					</div>
					)}
				</div>
				</div>
			))}

			{loading && (
				<div className="loading-message">
				<div className="loading-dots">
					<span></span>
					<span></span>
					<span></span>
				</div>
				AI is processing your request...
				</div>
			)}

			{error && <div className="error-message">{error}</div>}
			</section>

			<form className="input-container" onSubmit={handleSendMessage}>
			<input
				type="text"
				placeholder="Ask anything about your inventory..."
				value={input}
				onChange={(e) => setInput(e.target.value)}
				disabled={loading}
			/>

			<button type="submit" disabled={loading || !input.trim()}>
				Send ↑
			</button>
			</form>

			<footer className="chat-footer">
			AI-generated responses may require verification.
			</footer>
		</main>
		</div>
	);
}

export default App;

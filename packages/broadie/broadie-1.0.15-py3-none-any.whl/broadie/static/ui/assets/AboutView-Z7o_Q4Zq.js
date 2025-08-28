import{c as e,d as t,e as n,f as r}from"./index-CLI-I4Lj.js";const i={name:`AboutView`},a={class:`container`};function o(e,i,o,s,c,l){return r(),t(`div`,a,[...i[0]||=[n(`<div class="card" style="margin-bottom:16px;" data-v-33be640d><div class="card-header" data-v-33be640d>About Broadie</div><div class="card-body" data-v-33be640d><p data-v-33be640d> Broadie is a batteries-included multi-agent framework with REST and WebSocket APIs, persistent memory, and a flexible tool system. This UI lets you chat with your agent, view conversations, and stream responses. </p></div></div><div class="card" style="margin-bottom:16px;" data-v-33be640d><div class="card-header" data-v-33be640d>Quick Start — Create and Run an Agent</div><div class="card-body" data-v-33be640d><ol class="small" style="line-height:1.7;" data-v-33be640d><li data-v-33be640d> Install Broadie (from PyPI): <pre class="mono" data-v-33be640d><code data-v-33be640d>pip install broadie</code></pre></li><li data-v-33be640d> Create a minimal agent config file <strong data-v-33be640d>main.json</strong>: <pre class="mono" data-v-33be640d><code data-v-33be640d>{
  &quot;name&quot;: &quot;my_agent&quot;,
  &quot;description&quot;: &quot;A helpful assistant&quot;,
  &quot;instruction&quot;: &quot;You are a helpful AI assistant.&quot;,
  &quot;model&quot;: {&quot;provider&quot;: &quot;google&quot;, &quot;name&quot;: &quot;gemini-2.0-flash&quot;}
}</code></pre></li><li data-v-33be640d> Run the agent directly (CLI): <pre class="mono" data-v-33be640d><code data-v-33be640d>broadie run main.json</code></pre></li><li data-v-33be640d> Or serve the API + UI: <pre class="mono" data-v-33be640d><code data-v-33be640d>broadie serve main.json</code></pre> Then open the UI at: <pre class="mono" data-v-33be640d><code data-v-33be640d>http://localhost:8000/</code></pre></li></ol><p class="small muted" data-v-33be640d> Tip: copy .env.example to .env and configure your model keys (e.g., GOOGLE_API_KEY). </p></div></div><div class="card" data-v-33be640d><div class="card-header" data-v-33be640d>Programmatic Agent (Optional)</div><div class="card-body" data-v-33be640d><p class="small" data-v-33be640d>Define your agent in Python and serve it:</p><pre class="mono" data-v-33be640d><code data-v-33be640d>from broadie import Agent, tool

@tool(name=&quot;echo&quot;, description=&quot;Echo input&quot;)
def echo(text: str) -&gt; str:
    return text

class EchoAgent(Agent):
    def build_config(self):
        return {&quot;name&quot;: &quot;echo_agent&quot;, &quot;instruction&quot;: &quot;Echoer&quot;}

# Serve from code
# broadie serve module.path:EchoAgent
</code></pre></div></div>`,3)]])}var s=e(i,[[`render`,o],[`__scopeId`,`data-v-33be640d`]]);export{s as default};
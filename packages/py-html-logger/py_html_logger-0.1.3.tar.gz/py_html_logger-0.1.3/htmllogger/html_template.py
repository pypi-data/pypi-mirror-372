html_header = r"""<!DOCTYPE html>
<meta charset="utf-8" />

<style>
  body {
    color: white;
    background-color: black;
    font-family: monospace, sans-serif;
    margin: 0;
    padding: 0;
  }
  .filter-panel {
    display: none;
    position: fixed;
    top: 80px;
    right: 20px;
    background-color: #2c2c2c;
    border: 1px solid #444;
    padding: 15px;
    border-radius: 8px;
    z-index: 1000;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
    width: 350px;
    max-height: 80vh;
    overflow-y: auto;
  }
  .filter-tabs {
    display: flex;
    margin-bottom: 10px;
    border-bottom: 1px solid #444;
  }
  .filter-tab {
    padding: 8px 15px;
    cursor: pointer;
    background: none;
    border: none;
    color: #ccc;
    flex: 1;
    text-align: center;
  }
  .filter-tab.active {
    color: #4caf50;
    border-bottom: 2px solid #4caf50;
  }
  .filter-content {
    display: none;
  }
  .filter-content.active {
    display: block;
  }
  .filter-input {
    width: 100%;
    padding: 8px;
    background-color: #1a1a1a;
    color: white;
    border: 1px solid #444;
    border-radius: 4px;
    margin-bottom: 10px;
    box-sizing: border-box;
  }
  .filter-help {
    font-size: 12px;
    color: #888;
    margin-bottom: 10px;
  }
  .filter-types {
    max-height: 200px;
    overflow-y: auto;
    margin-bottom: 10px;
  }
  .type-checkbox {
    margin: 5px 0;
    display: block;
  }
  .type-checkbox input {
    margin-right: 8px;
  }
  .filter-btn {
    position: fixed;
    top: 20px;
    right: 20px;
    background-color: rgba(200, 200, 200, 0.8); /* Cinza claro com transparência */
    color: #333;
    border: none;
    border-radius: 8px; /* Cantos arredondados (não mais circular) */
    width: 50px;
    height: 50px;
    font-size: 24px;
    cursor: pointer;
    z-index: 1000;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    transition: background-color 0.3s;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .filter-btn:hover {
    background-color: rgba(180, 180, 180, 0.9); /* Cinza um pouco mais escuro no hover */
  }
  .highlight {
    background-color: yellow;
    color: black;
    padding: 0 2px;
  }
  .log-line {
    margin: 2px 0;
  }
  .visible {
    display: block;
  }
  .hidden {
    display: none;
  }
  .filter-actions {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
  }
  .filter-action-btn {
    padding: 6px 12px;
    background-color: #4caf50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  .filter-action-btn.clear {
    background-color: #f44336;
  }

  .filter-footer {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 15px;
    border-top: 1px solid #444;
    padding-top: 10px;
  }

  .filter-action-btn {
    padding: 8px 16px;
    font-size: 14px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: background-color 0.2s, transform 0.1s;
  }

  .filter-action-btn:hover {
    transform: translateY(-1px);
  }

  .filter-action-btn.apply {
    background-color: #4caf50;
    color: white;
  }

  .filter-action-btn.clear {
    background-color: #f44336;
    color: white;
  }

  #filteredContainer .log-line {
    display: block;
    margin: 2px 0;
  }

</style>

<body>
  <div id="filterPanel" class="filter-panel">
    <div class="filter-tabs">
      <button class="filter-tab active" data-tab="text">Filtro de Texto</button>
      <button class="filter-tab" data-tab="type">Filtro por Tipo</button>
    </div>

    <div id="textFilter" class="filter-content active">
      <input
        type="text"
        id="textFilterInput"
        class="filter-input"
        placeholder="Digite para filtrar (usar AND, OR)..."
      />
      <div class="filter-help">
        Use AND, OR para filtros complexos. Ex: "error AND security", "warning
        OR info"
      </div>
    </div>

    <div id="typeFilter" class="filter-content">
      <div id="typeFilterList" class="filter-types">
        <!-- Checkboxes gerados dinamicamente -->
      </div>
      <div class="filter-actions">
        <button id="selectAllTypes" class="filter-action-btn apply">
          Selecionar Todos
        </button>
        <button id="deselectAllTypes" class="filter-action-btn clear">
          Limpar Seleção
        </button>
      </div>
    </div>

    <!-- Rodapé com botões principais -->
    <div class="filter-footer">
      <button id="applyFiltersBtn" class="filter-action-btn apply">
        Aplicar
      </button>
      <button id="clearFiltersBtn" class="filter-action-btn clear">
        Resetar
      </button>
    </div>
  </div>

  <button id="filterBtn" class="filter-btn">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 4H21L14 12V20L10 22V12L3 4Z" stroke="#333333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </button>
  <div id="filteredContainer"></div>

  <div id="logContainer">
    <font color="white">
      <!-- LOG_CONTENT -->
    </font>
  </div>
  <script>
    // Variável para armazenar as tags usadas
    let USED_TAGS = [];
    let activeFilters = { text: "", types: [] };

    // Função para extrair tags do DOM - CORRIGIDA
    function extractTagsFromDOM() {
      const tagSet = new Set();
      // Selecionar apenas elementos dentro do container de logs
      const elements = document.querySelectorAll("#logContainer [data-tags]");
      elements.forEach((element) => {
        const tags = element.getAttribute("data-tags").split(",");
        tags.forEach((tag) => tagSet.add(tag.trim()));
      });
      USED_TAGS = Array.from(tagSet).sort();
    }

    document.getElementById("applyFiltersBtn").addEventListener("click", function () {
      activeFilters.text = document.getElementById("textFilterInput").value;
      activeFilters.types = Array.from(
        document.querySelectorAll("#typeFilterList input:checked")
      ).map((cb) => cb.value);
      applyFilters();
    });

    document.getElementById("clearFiltersBtn").addEventListener("click", clearFilters);

    // Inicializar a lista de tipos
    function initTypeFilter() {
      const typeFilterList = document.getElementById("typeFilterList");
      typeFilterList.innerHTML = "";
      USED_TAGS.forEach((tag) => {
        const label = document.createElement("label");
        label.className = "type-checkbox";
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.value = tag;
        // checkbox.addEventListener("change", updateTypeFilter);
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(tag));
        typeFilterList.appendChild(label);
      });
    }

    // Alternar abas
    function setupTabs() {
      const tabs = document.querySelectorAll(".filter-tab");
      const tabContents = document.querySelectorAll(".filter-content");
      tabs.forEach((tab) => {
        tab.addEventListener("click", function () {
          const tabName = this.getAttribute("data-tab");

          // Ativar aba clicada
          tabs.forEach((t) => t.classList.remove("active"));
          this.classList.add("active");

          // Mostrar conteúdo correspondente
          tabContents.forEach((content) => content.classList.remove("active"));
          document.getElementById(`${tabName}Filter`).classList.add("active");

          // Focar no input da aba ativa
          if (tabName === "text") {
            document.getElementById("textFilterInput").focus();
          }
        });
      });
    }

    // Atualizar filtro de tipos
    function updateTypeFilter() {
      activeFilters.types = Array.from(
        document.querySelectorAll("#typeFilterList input:checked")
      ).map((checkbox) => checkbox.value);
      applyFilters();
    }

    function applyFilters() {
      const lines = document.querySelectorAll("#logContainer [data-tags]");
      const filteredContainer = document.getElementById("filteredContainer");

      const textRaw = (activeFilters.text || "").trim();
      const hasTextFilter = textRaw !== "";
      const hasTypeFilter =
        Array.isArray(activeFilters.types) && activeFilters.types.length > 0;

      // Se não há filtros: restaura todas as linhas e limpa resultados
      if (!hasTextFilter && !hasTypeFilter) {
        lines.forEach((line) => {
          if (!line.hasAttribute("data-original-html")) {
            line.setAttribute("data-original-html", line.innerHTML);
          }
          const originalHtml = line.getAttribute("data-original-html");
          line.innerHTML = originalHtml;
        });
        filteredContainer.innerHTML = "";
        return;
      }

      // Preparar filtros de texto (case-insensitive) com AND/OR
      let textFilters = [];
      let isAnd = false;
      if (hasTextFilter) {
        const lower = textRaw.toLowerCase();
        if (/\sand\s/i.test(lower)) {
          textFilters = lower
            .split(/\sand\s/i)
            .map((s) => s.trim())
            .filter(Boolean);
          isAnd = true;
        } else if (/\sor\s/i.test(lower)) {
          textFilters = lower
            .split(/\sor\s/i)
            .map((s) => s.trim())
            .filter(Boolean);
        } else {
          textFilters = [lower];
        }
      }

      // Começa com o container de resultados limpo para evitar duplicações
      filteredContainer.innerHTML = "";

      lines.forEach((line) => {
        // Garantir HTML original salvo e restaurar antes de destacar novamente
        if (!line.hasAttribute("data-original-html")) {
          line.setAttribute("data-original-html", line.innerHTML);
        }
        const originalHtml = line.getAttribute("data-original-html");
        line.innerHTML = originalHtml;

        const textContent = (
          line.textContent ||
          line.innerText ||
          ""
        ).toLowerCase();
        const lineTags = (line.getAttribute("data-tags") || "")
          .split(",")
          .map((t) => t.trim())
          .filter(Boolean);

        // Texto
        let textMatch = !hasTextFilter;
        if (hasTextFilter) {
          if (isAnd) {
            textMatch = textFilters.every((f) => textContent.includes(f));
          } else {
            textMatch = textFilters.some((f) => textContent.includes(f));
          }
        }

        // Tipos (tags)
        const typeMatch =
          !hasTypeFilter ||
          activeFilters.types.some((t) => lineTags.includes(t));

        if (textMatch && typeMatch) {
          // Destacar no original (se houver filtro de texto)
          if (hasTextFilter) {
            let highlighted = originalHtml;
            textFilters.forEach((f) => {
              if (!f) return;
              const regex = new RegExp(
                f.replace(/[.*+?^${}()|[\\]\\]/g, "\$&"),
                "gi"
              );
              highlighted = highlighted.replace(
                regex,
                (m) => `<span class="highlight">${m}</span>`
              );
            });
            line.innerHTML = highlighted;
          }

          const wrapper = document.createElement("div");
          wrapper.className = "log-line";
          const copy = line.cloneNode(true);
          wrapper.appendChild(copy);
          filteredContainer.appendChild(wrapper);
        }
      });
      if (!hasTextFilter && !hasTypeFilter) {
        // Mostrar log original
        document.getElementById("logContainer").style.display = "block";
        document.getElementById("filteredContainer").style.display = "none";
      } else {
        // Mostrar apenas o agrupado
        document.getElementById("logContainer").style.display = "none";
        document.getElementById("filteredContainer").style.display = "block";
      }
    }

    function clearFilters() {
      document.getElementById("textFilterInput").value = "";
      // document.querySelectorAll("#typeFilterList input").forEach((cb) => (cb.checked = false));
      activeFilters = { text: "", types: [] };

      // Restaura linhas originais
      document.querySelectorAll("#logContainer [data-tags]").forEach((line) => {
        if (line.hasAttribute("data-original-html")) {
          line.innerHTML = line.getAttribute("data-original-html");
        }
      });

      // Mostrar log original novamente
      document.getElementById("logContainer").style.display = "block";
      document.getElementById("filteredContainer").style.display = "none";
      document.getElementById("filteredContainer").innerHTML = "";
    }

    document.addEventListener("DOMContentLoaded", function () {
      const filterBtn = document.getElementById("filterBtn");
      const filterPanel = document.getElementById("filterPanel");
      const textFilterInput = document.getElementById("textFilterInput");
      const selectAllBtn = document.getElementById("selectAllTypes");
      const deselectAllBtn = document.getElementById("deselectAllTypes");
      
      // Extrair tags e inicializar filtros
      extractTagsFromDOM();
      initTypeFilter();
      setupTabs();
      
      // Alternar visibilidade do painel de filtro
      filterBtn.addEventListener("click", function () {
        if (filterPanel.style.display === "block") {
          filterPanel.style.display = "none";
        } else {
          // Atualizar tags ao abrir o painel
          extractTagsFromDOM();
          initTypeFilter();
          filterPanel.style.display = "block";
          // Focar no input da aba ativa
          const activeTab = document
            .querySelector(".filter-tab.active")
            .getAttribute("data-tab");
          if (activeTab === "text") {
            textFilterInput.focus();
          }
        }
      });
      
      // Selecionar todos os tipos
      selectAllBtn.addEventListener("click", function () {
        document.querySelectorAll("#typeFilterList input").forEach((checkbox) => {
            checkbox.checked = true;
          });
      });
      
      // Descelecionar todos os tipos
      deselectAllBtn.addEventListener("click", function () {
        document.querySelectorAll("#typeFilterList input").forEach((checkbox) => {
            checkbox.checked = false;
          });
      });
      
      // Fechar o painel se clicar fora dele
      document.addEventListener("click", function (event) {
        if (!filterPanel.contains(event.target) && !filterBtn.contains(event.target)) {
          filterPanel.style.display = "none";
        }
      });
      
      // Impedir que cliques dentro do painel fechem ele
      filterPanel.addEventListener("click", function (event) {
        event.stopPropagation();
      });

      textFilterInput.addEventListener("keypress", function (e) {
        if (e.key === "Enter") {
          document.getElementById("applyFiltersBtn").click();
        }
      });
    });
  </script>
  
</body>

"""

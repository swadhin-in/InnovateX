document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById("sidebar");
    const mainContent = document.getElementById("main");
    const toggleSidebarBtn = document.getElementById("toggleSidebar");
    const sidebarLinks = document.querySelectorAll(".sidebar a");
    const dashboardCards = document.querySelectorAll(".card[data-card]");
    const tabContents = document.querySelectorAll(".tab-content");
    const downloadPdfBtn = document.getElementById("downloadPdfBtn");

    // Function to show a specific tab
    function showTab(tabId) {
        // Hide all tab contents
        tabContents.forEach(content => {
            content.classList.remove("active");
        });

        // Show the requested tab
        const activeTab = document.getElementById(tabId);
        if (activeTab) {
            activeTab.classList.add("active");
        }
    }

    // Function to update sidebar active state
    function updateSidebarActive(tabId) {
        sidebarLinks.forEach(link => {
            link.classList.remove("active");
            if (link.dataset.tab === tabId.replace('-tab', '')) {
                link.classList.add("active");
            }
        });
    }

    // Toggle sidebar visibility
    toggleSidebarBtn.addEventListener("click", () => {
        sidebar.classList.toggle("active");
        mainContent.classList.toggle("shift");
    });

    // Handle sidebar navigation
    sidebarLinks.forEach(link => {
        link.addEventListener("click", function (e) {
            e.preventDefault();
            const tabId = this.dataset.tab + "-tab";
            showTab(tabId);
            updateSidebarActive(tabId);
        });
    });

    // Handle dashboard card clicks
    dashboardCards.forEach(card => {
        card.addEventListener("click", function () {
            const tabId = this.dataset.card + "-tab";
            showTab(tabId);
            updateSidebarActive(tabId);
        });
    });

    // Handle PDF download button
    if (downloadPdfBtn) {
        downloadPdfBtn.addEventListener("click", () => {
            window.print();
        });
    }

    // Initial state: show dashboard tab
    showTab("dashboard-tab");
});
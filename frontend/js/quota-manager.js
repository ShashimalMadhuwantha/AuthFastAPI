/**
 * Quota Management System
 * Handles data quota limits, checking, and enforcement
 */

// Current quota limit (stored in localStorage)
let currentQuotaLimit = parseInt(localStorage.getItem('quotaLimit')) || 25000;

// Initialize quota limit on page load
document.addEventListener('DOMContentLoaded', () => {
    const quotaInput = document.getElementById('quotaLimit');
    if (quotaInput) {
        quotaInput.value = currentQuotaLimit;
    }

    const quotaDisplay = document.getElementById('quotaLimitDisplay');
    if (quotaDisplay) {
        quotaDisplay.textContent = currentQuotaLimit.toLocaleString();
    }
});

/**
 * Refresh quota statistics from backend
 */
async function refreshQuotaStats(startDate = null, endDate = null) {
    try {
        const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');

        // Build URL with optional date range
        let url = `${API_CONFIG.BASE_URL}/api/v1/quota/stats?quota_limit=${currentQuotaLimit}`;
        if (startDate && endDate) {
            url += `&start_date=${startDate}&end_date=${endDate}`;
        }

        const response = await fetch(url, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = 'index.html';
                return;
            }
            throw new Error('Failed to fetch quota stats');
        }

        const result = await response.json();
        const stats = result.data;

        // Update UI elements
        document.getElementById('quotaCurrentPoints').textContent = stats.total_data_points.toLocaleString();
        document.getElementById('quotaLimitDisplay').textContent = stats.quota_limit.toLocaleString();
        document.getElementById('quotaUsagePercent').textContent = stats.usage_percent + '%';

        // Update progress bar
        const progressBar = document.getElementById('quotaProgressBar');
        progressBar.style.width = Math.min(stats.usage_percent, 100) + '%';

        // Change color based on usage
        if (stats.usage_percent >= 100) {
            progressBar.style.background = '#ef4444'; // Red
        } else if (stats.usage_percent >= 80) {
            progressBar.style.background = '#f59e0b'; // Orange
        } else {
            progressBar.style.background = '#047857'; // Green
        }

        // Show/hide warning
        const warning = document.getElementById('quotaWarning');
        if (stats.quota_exceeded) {
            warning.style.display = 'block';
            let message = `You have ${stats.total_data_points.toLocaleString()} data points`;
            if (stats.date_range_applied) {
                message += ` in the selected date range`;
            }
            message += `. Quota limit is ${stats.quota_limit.toLocaleString()}.`;
            document.getElementById('quotaWarningMessage').textContent = message;
        } else {
            warning.style.display = 'none';
        }

        // Show date range info if applied
        const quotaStatsDiv = document.getElementById('quotaStats');
        let rangeInfo = quotaStatsDiv.querySelector('.quota-range-info');
        if (stats.date_range_applied) {
            if (!rangeInfo) {
                rangeInfo = document.createElement('div');
                rangeInfo.className = 'quota-range-info';
                rangeInfo.style.cssText = 'margin-top: 12px; padding: 8px; background: #eff6ff; border-radius: 6px; font-size: 12px; color: #1e40af;';
                quotaStatsDiv.appendChild(rangeInfo);
            }
            rangeInfo.textContent = `📅 Showing stats for selected date range`;
        } else {
            if (rangeInfo) {
                rangeInfo.remove();
            }
        }

        console.log('📊 Quota stats refreshed:', stats);

    } catch (error) {
        console.error('❌ Error fetching quota stats:', error);
        document.getElementById('quotaCurrentPoints').textContent = 'Error';
    }
}

/**
 * Refresh quota stats with current date range from localStorage
 */
function refreshQuotaStatsWithCurrentRange() {
    const customStartDate = localStorage.getItem('customStartDate');
    const customEndDate = localStorage.getItem('customEndDate');

    if (customStartDate && customEndDate) {
        const start = new Date(customStartDate);
        const end = new Date(customEndDate);
        const startISO = start.toISOString().slice(0, 19);
        const endISO = end.toISOString().slice(0, 19);
        refreshQuotaStats(startISO, endISO);
    } else {
        refreshQuotaStats();
    }
}

/**
 * Update quota limit with smart date range adjustment
 */
async function updateQuotaLimit() {
    const newLimit = parseInt(document.getElementById('quotaLimit').value);

    if (isNaN(newLimit) || newLimit < 1000) {
        if (window.customModal) {
            window.customModal.error('Invalid Quota', 'Quota limit must be at least 1,000 data points.');
        } else {
            alert('⚠️ Quota limit must be at least 1,000 data points');
        }
        document.getElementById('quotaLimit').value = currentQuotaLimit;
        return;
    }

    currentQuotaLimit = newLimit;
    localStorage.setItem('quotaLimit', newLimit);
    document.getElementById('quotaLimitDisplay').textContent = newLimit.toLocaleString();

    console.log(`✅ Quota limit updated to ${newLimit.toLocaleString()}`);

    // Check if current date range exceeds new quota
    const customStartDate = localStorage.getItem('customStartDate');
    const customEndDate = localStorage.getItem('customEndDate');

    if (customStartDate && customEndDate) {
        const start = new Date(customStartDate);
        const end = new Date(customEndDate);
        const startISO = start.toISOString().slice(0, 19);
        const endISO = end.toISOString().slice(0, 19);

        // Check quota for current range
        try {
            const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
            const response = await fetch(
                `${API_CONFIG.BASE_URL}/api/v1/quota/check-date-range?start_date=${startISO}&end_date=${endISO}&quota_limit=${newLimit}`,
                { headers: { 'Authorization': `Bearer ${token}` } }
            );

            if (response.ok) {
                const result = await response.json();
                const data = result.data;

                if (data.would_exceed) {
                    // Calculate how many days the quota covers
                    const totalDays = (end - start) / (1000 * 60 * 60 * 24);
                    const quotaRatio = newLimit / data.data_points_in_range;
                    const coveredDays = Math.max(1, Math.floor(totalDays * quotaRatio));

                    // Show warning
                    if (window.customModal) {
                        const proceed = await window.customModal.confirm(
                            '⚠️ Quota Prioritized Over Date Range',
                            `<div style="text-align: left; line-height: 1.6;">
                                <p style="margin-bottom: 12px;">Your new quota of <strong>${newLimit.toLocaleString()}</strong> data points is less than the selected date range.</p>
                                <div style="background: #fef2f2; padding: 12px; border-radius: 6px; margin: 12px 0; border-left: 4px solid #ef4444;">
                                    <p style="margin: 0; color: #991b1b; font-size: 13px;">
                                        <strong>Selected range:</strong> ${totalDays.toFixed(1)} days (${data.data_points_in_range.toLocaleString()} points)<br>
                                        <strong>Quota covers:</strong> ~${coveredDays} days (${newLimit.toLocaleString()} points)
                                    </p>
                                </div>
                                <div style="background: #eff6ff; padding: 12px; border-radius: 6px; margin: 12px 0; border-left: 4px solid #2563eb;">
                                    <p style="margin: 0; color: #1e40af; font-size: 13px;">
                                        <strong>📊 Quota Priority:</strong> System will show most recent ${coveredDays} days
                                    </p>
                                </div>
                                <p style="margin: 0; font-size: 14px;">Adjust date range to the most recent <strong>${coveredDays} days</strong>?</p>
                            </div>`,
                            '⚠️',
                            { confirmText: `Adjust to ${coveredDays} Days`, cancelText: 'Keep Current Range' }
                        );

                        if (proceed) {
                            // Adjust date range
                            const newStart = new Date(end);
                            newStart.setDate(newStart.getDate() - coveredDays);

                            const newStartStr = newStart.toISOString().slice(0, 16);
                            const newEndStr = end.toISOString().slice(0, 16);
                            localStorage.setItem('customStartDate', newStartStr);
                            localStorage.setItem('customEndDate', newEndStr);

                            // Update UI
                            const startInput = document.getElementById('startDateTime');
                            const endInput = document.getElementById('endDateTime');
                            if (startInput) startInput.value = newStartStr;
                            if (endInput) endInput.value = newEndStr;

                            console.log(`📅 Date range adjusted to last ${coveredDays} days`);

                            await window.customModal.success(
                                'Date Range Adjusted',
                                `Dashboard now showing the most recent ${coveredDays} days within your quota.`
                            );
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Error checking quota:', error);
        }
    }

    // Refresh stats
    refreshQuotaStatsWithCurrentRange();
}

/**
 * Check if a date range would exceed the quota
 */
async function checkDateRangeQuota(startDate, endDate) {
    try {
        const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
        const response = await fetch(
            `${API_CONFIG.BASE_URL}/api/v1/quota/check-date-range?start_date=${startDate}&end_date=${endDate}&quota_limit=${currentQuotaLimit}`,
            { headers: { 'Authorization': `Bearer ${token}` } }
        );

        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = 'index.html';
                return false;
            }
            throw new Error('Failed to check date range quota');
        }

        const result = await response.json();
        const data = result.data;

        if (data.would_exceed) {
            let proceed;

            if (window.customModal) {
                proceed = await window.customModal.quotaWarning(data);
            } else {
                proceed = confirm(`Quota exceeded. Increase to ${data.suggested_quota.toLocaleString()}?`);
            }

            if (proceed) {
                document.getElementById('quotaLimit').value = data.suggested_quota;
                await updateQuotaLimit();

                if (window.customModal) {
                    await window.customModal.success(
                        'Quota Updated',
                        `Quota increased to ${data.suggested_quota.toLocaleString()} DPM.`
                    );
                }
                return true;
            } else {
                if (window.customModal) {
                    await window.customModal.error(
                        'Date Range Not Applied',
                        'Please select a smaller date range or increase your quota.'
                    );
                }
                return false;
            }
        }

        return true;

    } catch (error) {
        console.error('❌ Error checking quota:', error);
        return true; // Fail-open
    }
}

// Export for use in other scripts
window.quotaManager = {
    refreshQuotaStats,
    updateQuotaLimit,
    checkDateRangeQuota,
    getCurrentQuotaLimit: () => currentQuotaLimit
};

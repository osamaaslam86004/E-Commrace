const countDay = new Date(Date.UTC(2025, 2, 11, 23, 30, 0) - (5 * 60 * 60 * 1000)); // UTC+5

const countDown = () => {
    const now = new Date();
    const counter = countDay - now; // Define `counter` before using it

    if (counter < 0) {
        document.querySelector(".day").innerText = "00 Days";
        document.querySelector(".hour").innerText = "00 Hours";
        document.querySelector(".minute").innerText = "00 Minutes";
        document.querySelector(".second").innerText = "00 Seconds";
        return;
    }

    const second = 1000;
    const minute = second * 60;
    const hour = minute * 60;
    const day = hour * 24;

    const textDay = Math.floor(counter / day);
    const textHour = Math.floor((counter % day) / hour);
    const textMinute = Math.floor((counter % hour) / minute);
    const textSecond = Math.floor((counter % minute) / second);

    document.querySelector(".day").innerText = textDay + ' Days';
    document.querySelector(".hour").innerText = textHour + ' Hours';
    document.querySelector(".minute").innerText = textMinute + ' Minutes';
    document.querySelector(".second").innerText = textSecond + ' Seconds';
};

// Run immediately on page load
countDown();
// Update every second
setInterval(countDown, 1000);

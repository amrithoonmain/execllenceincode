// DOM Elements
const loginBtn = document.querySelector('.login-btn');
const adminBtn = document.querySelector('.admin-btn');
const loginModal = document.getElementById('loginModal');
const loginForm = document.getElementById('loginForm');
const navLinks = document.querySelectorAll('.nav-links a');
const sections = document.querySelectorAll('section');

// Event Listeners
loginBtn.addEventListener('click', () => {
    loginModal.style.display = 'block';
});

adminBtn.addEventListener('click', () => {
    loginModal.style.display = 'block';
});

loginModal.addEventListener('click', (e) => {
    if (e.target === loginModal) {
        loginModal.style.display = 'none';
    }
});

loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    // Add login logic here
    loginModal.style.display = 'none';
});

// Navigation
navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Remove active class from all links
        navLinks.forEach(link => {
            link.parentElement.classList.remove('active');
        });
        
        // Add active class to clicked link
        link.parentElement.classList.add('active');
        
        // Show corresponding section
        const targetId = link.getAttribute('href').substring(1);
        sections.forEach(section => {
            section.classList.remove('active');
            if (section.id === targetId) {
                section.classList.add('active');
            }
        });
    });
});

// Function to fetch books from the backend API
async function fetchBooks() {
    try {
        const response = await axios.get('http://localhost:5000/api/books');
        return response.data;
    } catch (error) {
        console.error('Error fetching books:', error);
        return [];
    }
}

// Function to create book cards
function createBookCard(book) {
    const card = document.createElement('div');
    card.className = 'book-card';
    card.innerHTML = `
        <div class="book-cover">
            <div class="book-spine"></div>
        </div>
        <div class="book-info">
            <h3>${book.title}</h3>
            <p>Author: ${book.author}</p>
            <p>Year: ${book.year}</p>
            <p class="status ${book.status}">${book.status}</p>
            <button class="issue-btn" ${book.status === 'issued' ? 'disabled' : ''}>
                ${book.status === 'issued' ? 'Issued' : 'Issue Book'}
            </button>
        </div>
    `;
    return card;
}

// Function to render books
function renderBooks(books) {
    const booksGrid = document.querySelector('.books-grid');
    booksGrid.innerHTML = '';
    books.forEach(book => {
        booksGrid.appendChild(createBookCard(book));
    });
}

// Initial render
fetchBooks().then(books => {
    renderBooks(books);
});

// Search functionality
const searchInput = document.querySelector('.search-bar input');
searchInput.addEventListener('input', async (e) => {
    const searchTerm = e.target.value.toLowerCase();
    const books = await fetchBooks();
    const filteredBooks = books.filter(book => 
        book.title.toLowerCase().includes(searchTerm) ||
        book.author.toLowerCase().includes(searchTerm) ||
        book.id.toString().includes(searchTerm)
    );
    renderBooks(filteredBooks);
});

// Function to fetch statistics from the backend API
async function fetchStats() {
    try {
        const response = await axios.get('http://localhost:5000/api/stats');
        return response.data;
    } catch (error) {
        console.error('Error fetching stats:', error);
        return { totalBooks: 0, issuedBooks: 0 };
    }
}

// Update stats
function updateStats(stats) {
    document.querySelector('.stat-card:nth-child(1) p').textContent = stats.totalBooks;
    document.querySelector('.stat-card:nth-child(3) p').textContent = stats.issuedBooks;
}

// Initial stats update
fetchStats().then(stats => {
    updateStats(stats);
});

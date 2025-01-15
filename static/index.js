
const apiBaseUrl = "http://127.0.0.1:8000";

// Fetch books and populate the table
//非同步從伺服器取得書籍列表，動態顯示在網頁表格
async function fetchBooks() { 
    //javascript的fetch API 發送HTTP GET請求，用awit等待fetch 回傳一個Promise一個Promise
    const response = await fetch(`${apiBaseUrl}/books`); 
    const books = await response.json();
    
    //根據Id "booksTable" 找到網頁中的HTML元素，並將該元素賦值給 const booksTable
    const booksTable = document.getElementById("booksTable");
    //將表格元素的內容設為空字串/清空現有的HTML
    booksTable.innerHTML = "";
    //迭代books並生成表格
    books.forEach(book => {
    const row = `<tr>
        <td>${book.id}</td>
        <td>${book.title}</td>
        <td>${book.author}</td>
        <td>${book.description || ""}</td>
        <td>
        <button onclick="deleteBook(${book.id})">Delete</button>
        <button onclick="updateBook(${book.id})">Edit</button>
        </td>
    </tr>`;
    booksTable.innerHTML += row;
    });
}

// Add a new book
// 用事件監聽器監聽id 為"addBookForm"表單的"submit"事件，當使用者按下提交按鈕會觸發此監聽器
// e.preventDefault() 阻止表單提交的預設行為，預設行為通常式重載頁面
document.getElementById("addBookForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const book = {
    id: null, 
    title: document.getElementById("bookTitle").value,
    author: document.getElementById("bookAuthor").value,
    description: document.getElementById("bookDescription").value || null
    };
    await fetch(`${apiBaseUrl}/books`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(book)
    });
    fetchBooks();
});

// Delete a book
async function deleteBook(id) {
    const isconfirmed = window.confirm(`Are you sure you want to delete the book with ID ${id} ?`);
    if(isconfirmed){
        await fetch(`${apiBaseUrl}/books/${id}`, { method: "DELETE" });
        // alert(`Book with ID ${id} has been deleted.`)
        fetchBooks();
    }
    // else{
    //     alert('Deletion canceled')
    // }
    
    
    
}

// Update a book (mock example, not interactive in UI)
async function updateBook(id) {
    const updatedBook = {
    id: id,
    title: prompt("New Title:"),
    author: prompt("New Author:"),
    description: prompt("New Description:") || null
    };
    
    await fetch(`${apiBaseUrl}/books/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updatedBook)
    });
    fetchBooks();
}

// Initial fetch
fetchBooks();
